// durable.js - Durable Objects give single-threaded, strongly consistent state.
// KV is eventually consistent, so it must NOT hold attempt counters, OTP single-use
// flags, or order state machines. That was the root flaw in the original lockout.
import { randomOtp, randomHex, hmacHex, safeEqual } from "./crypto.js";

const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json" } });

const OTP_TTL_MS = 5 * 60e3;
const MAX_FAILS = 3;
const LOCK_MS = 15 * 60e3;
const ISSUE_LIMIT = 3;
const ISSUE_WINDOW_MS = 10 * 60e3;
const DAY = 864e5;
export const REFUND_WINDOW_DAYS = 5;

// One instance per identity hash. Holds OTP hash, fail counter, lock, issue history.
export class OtpGuard {
  constructor(state, env) { this.s = state.storage; this.env = env; }
  async fetch(req) {
    const { op, identity, otp } = await req.json();
    const now = Date.now();
    const lockedUntil = (await this.s.get("lockedUntil")) || 0;
    if (now < lockedUntil) return json({ ok: false, reason: "LOCKED", retry_after_s: Math.ceil((lockedUntil - now) / 1000) }, 429);

    if (op === "issue") {
      const issues = ((await this.s.get("issues")) || []).filter((t) => now - t < ISSUE_WINDOW_MS);
      if (issues.length >= ISSUE_LIMIT) return json({ ok: false, reason: "TOO_MANY_REQUESTS" }, 429);
      issues.push(now);
      const code = randomOtp();
      const salt = randomHex(16);
      const hash = await hmacHex(this.env.OTP_PEPPER, `${salt}:${identity}:${code}`);
      await this.s.put({ issues, otp: { salt, hash, exp: now + OTP_TTL_MS }, fails: 0 });
      return json({ ok: true, code }); // returned to the Worker only, never to the client
    }

    if (op === "verify") {
      const rec = await this.s.get("otp");
      let valid = false;
      if (rec && now < rec.exp && typeof otp === "string") {
        // Do the slow crypto FIRST, then run the check-and-update below as one contiguous
        // run of storage operations (no non-storage await between read and write).
        const h = await hmacHex(this.env.OTP_PEPPER, `${rec.salt}:${identity}:${otp}`);
        valid = safeEqual(h, rec.hash);
      }
      // ---- critical section: storage-only awaits ----
      const lockedNow = (await this.s.get("lockedUntil")) || 0;
      if (now < lockedNow) return json({ ok: false, reason: "LOCKED", retry_after_s: Math.ceil((lockedNow - now) / 1000) }, 429);
      if (valid) {
        const cur = await this.s.get("otp");
        if (cur && cur.salt === rec.salt) { // still the same, unconsumed code => consume exactly once
          await this.s.delete("otp");
          await this.s.put("fails", 0);
          return json({ ok: true });
        }
      }
      const fails = ((await this.s.get("fails")) || 0) + 1; // counted even if no OTP exists
      if (fails >= MAX_FAILS) {
        await this.s.put({ lockedUntil: now + LOCK_MS, fails: 0 });
        await this.s.delete("otp");
        return json({ ok: false, reason: "LOCKED", retry_after_s: LOCK_MS / 1000 }, 429);
      }
      await this.s.put("fails", fails);
      return json({ ok: false, reason: "INVALID_CODE" }, 401);
    }
    return json({ ok: false, reason: "BAD_OP" }, 400);
  }
}

// Fixed-window counter, one instance per (bucket, ip)
export class RateLimiter {
  constructor(state) { this.s = state.storage; }
  async fetch(req) {
    const { limit, windowMs } = await req.json();
    const now = Date.now();
    let w = (await this.s.get("w")) || { start: now, n: 0 };
    if (now - w.start >= windowMs) w = { start: now, n: 0 };
    w.n += 1;
    await this.s.put("w", w);
    return json({ allowed: w.n <= limit, remaining: Math.max(0, limit - w.n) }, w.n <= limit ? 200 : 429);
  }
}

// One instance per order id. The ONLY place an order changes state.
export class OrderLedger {
  constructor(state) { this.s = state.storage; }
  async fetch(req) {
    const b = await req.json();
    const now = Date.now();
    let o = await this.s.get("order");

    if (b.op === "create") {
      if (o) return json({ ok: false, reason: "EXISTS" }, 409);
      o = { ...b.order, status: "PENDING_PAYMENT", created_at: now, paid_at: null, release_at: null, refund: null };
      await this.s.put("order", o);
      return json({ ok: true, order: o }, 201);
    }
    if (!o) return json({ ok: false, reason: "NOT_FOUND" }, 404);

    if (b.op === "get") {
      if (o.uid !== b.uid) return json({ ok: false, reason: "NOT_FOUND" }, 404); // do not leak existence
      return json({ ok: true, order: o });
    }

    if (b.op === "confirm") { // called only from a signature-verified gateway webhook
      if (o.status !== "PENDING_PAYMENT") return json({ ok: true, order: o }); // idempotent
      if (b.amount_paise !== o.amount_paise) return json({ ok: false, reason: "AMOUNT_MISMATCH" }, 422);
      o.status = "HELD";
      o.paid_at = now;
      o.release_at = now + REFUND_WINDOW_DAYS * DAY;
      await this.s.put("order", o);
      return json({ ok: true, order: o });
    }

    if (b.op === "refund") {
      if (o.uid !== b.uid) return json({ ok: false, reason: "NOT_FOUND" }, 404);
      if (o.status === "HELD" && now >= o.release_at) { o.status = "RELEASED"; await this.s.put("order", o); }
      if (o.status === "REFUND_PENDING_PAYOUT" || o.status === "REFUNDED") return json({ ok: false, reason: "ALREADY_REFUNDED", order: o }, 409);
      if (o.status !== "HELD") return json({ ok: false, reason: "NOT_REFUNDABLE", status: o.status }, 409);
      // Amounts are computed server-side in integer paise. Client input is never trusted.
      const refund = Math.floor(o.amount_paise / 2);
      o.status = "REFUND_PENDING_PAYOUT";
      o.refund = { refund_paise: refund, retained_paise: o.amount_paise - refund, requested_at: now };
      await this.s.put("order", o);
      return json({ ok: true, order: o });
    }
    return json({ ok: false, reason: "BAD_OP" }, 400);
  }
}
