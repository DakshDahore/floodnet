import { randomHex, sha256Hex, hmacHex, safeEqual, encryptPII, decryptPII, normalizeIdentity, maskIdentity } from "./crypto.js";
import { runTacticalReasoning } from "./ai.js";
export { OtpGuard, RateLimiter, OrderLedger } from "./durable.js";

const PLANS = {
  free: { price_paise: 0, daily_quota: 10 },
  pro: { price_paise: 4900, daily_quota: 5000 },
  ultra: { price_paise: 14900, daily_quota: 100000 },
};
const TERMS_VERSION = "2026-11-v1"; // bump whenever the refund terms change
const SESSION_TTL_S = 86400;
const REQUIRED = ["OTP_PEPPER", "PII_KEY", "PAYMENT_WEBHOOK_SECRET", "OTP_WEBHOOK_URL", "OTP_WEBHOOK_TOKEN"];
const BINDINGS = ["FLOODLOCK_KV", "OTP_GUARD", "RATE_LIMITER", "ORDER_LEDGER"];

function corsHeaders(env, req) {
  const origin = req.headers.get("origin");
  const allowed = (env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  const h = { vary: "origin" };
  if (origin && allowed.includes(origin)) {
    h["access-control-allow-origin"] = origin;
    h["access-control-allow-methods"] = "GET,POST,OPTIONS";
    h["access-control-allow-headers"] = "content-type,authorization";
  }
  return h;
}
function reply(env, req, obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store", "x-content-type-options": "nosniff", ...corsHeaders(env, req) },
  });
}
async function callDO(ns, name, body) {
  const stub = ns.get(ns.idFromName(name));
  const r = await stub.fetch("https://do.internal/", { method: "POST", body: JSON.stringify(body) });
  return { status: r.status, data: await r.json() };
}
async function rateLimit(env, ip, bucket, limit, windowMs) {
  const r = await callDO(env.RATE_LIMITER, `${bucket}:${ip}`, { limit, windowMs });
  return r.data.allowed;
}
async function readBody(req, max = 4096) {
  const text = await req.text();
  if (text.length > max) throw Object.assign(new Error("too large"), { status: 413 });
  return text;
}
async function parseJson(req) {
  try { return JSON.parse((await readBody(req)) || "{}"); }
  catch (e) { throw Object.assign(new Error("bad json"), { status: e.status || 400 }); }
}

// Real session check: opaque random token, looked up server-side, expiry enforced.
async function getSession(env, req) {
  const m = (req.headers.get("authorization") || "").match(/^Bearer ([a-f0-9]{64})$/);
  if (!m) return null;
  const s = await env.FLOODLOCK_KV.get(`sess:${await sha256Hex(m[1])}`, "json");
  return s && s.exp > Date.now() ? s : null;
}

async function sendOtp(env, ident, code) {
  const r = await fetch(env.OTP_WEBHOOK_URL, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${env.OTP_WEBHOOK_TOKEN}` },
    body: JSON.stringify({ to: ident.value, channel: ident.kind, code }),
  });
  return r.ok;
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const path = url.pathname;
    try {
      if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(env, req) });
      if (path === "/health") return reply(env, req, { ok: true });

      const missing = [...REQUIRED.filter((k) => !env[k]), ...BINDINGS.filter((k) => !env[k])];
      if (missing.length) { console.error("CONFIG_ERROR missing:", missing.join(",")); return reply(env, req, { error: "CONFIG_ERROR" }, 503); }

      const ip = req.headers.get("cf-connecting-ip") || "unknown";
      if (!(await rateLimit(env, ip, "global", 60, 60e3))) return reply(env, req, { error: "RATE_LIMITED" }, 429);

      // ── POST /api/auth/send-otp
      if (path === "/api/auth/send-otp" && req.method === "POST") {
        if (!(await rateLimit(env, ip, "otp", 5, 60e3))) return reply(env, req, { error: "RATE_LIMITED" }, 429);
        const body = await parseJson(req);
        const ident = normalizeIdentity(body.email || body.phone);
        if (!ident) return reply(env, req, { error: "INVALID_IDENTITY" }, 400);
        const r = await callDO(env.OTP_GUARD, await sha256Hex(ident.value), { op: "issue", identity: ident.value });
        if (r.status === 429) return reply(env, req, { error: "TRY_LATER" }, 429);
        if (!(await sendOtp(env, ident, r.data.code))) return reply(env, req, { error: "DELIVERY_FAILED" }, 502);
        return reply(env, req, { success: true, message: "If the address is valid, a code has been sent.", expires_seconds: 300 });
      }

      // ── POST /api/auth/verify-otp
      if (path === "/api/auth/verify-otp" && req.method === "POST") {
        if (!(await rateLimit(env, ip, "otpv", 10, 60e3))) return reply(env, req, { error: "RATE_LIMITED" }, 429);
        const body = await parseJson(req);
        const ident = normalizeIdentity(body.email || body.phone);
        if (!ident || !/^\d{6}$/.test(String(body.otp || ""))) return reply(env, req, { error: "INVALID_REQUEST" }, 400);
        const r = await callDO(env.OTP_GUARD, await sha256Hex(ident.value), { op: "verify", identity: ident.value, otp: String(body.otp) });
        if (r.status === 429) return reply(env, req, { error: "LOCKED", retry_after_s: r.data.retry_after_s }, 429);
        if (!r.data.ok) return reply(env, req, { error: "INVALID_CODE" }, 401); // generic: no attempts-left oracle

        const idxKey = `uidx:${await hmacHex(env.OTP_PEPPER, `idx:${ident.value}`)}`;
        let uid = await env.FLOODLOCK_KV.get(idxKey);
        if (!uid) {
          uid = `USR_${randomHex(8)}`;
          await env.FLOODLOCK_KV.put(`user:${uid}`, JSON.stringify({
            uid, kind: ident.kind, plan: "free", created_at: Date.now(),
            identity_enc: await encryptPII(env, ident.value, uid),
          }));
          await env.FLOODLOCK_KV.put(idxKey, uid);
        }
        const token = randomHex(32);
        await env.FLOODLOCK_KV.put(`sess:${await sha256Hex(token)}`, JSON.stringify({ uid, exp: Date.now() + SESSION_TTL_S * 1000 }), { expirationTtl: SESSION_TTL_S });
        return reply(env, req, { session_token: token, expires_in: SESSION_TTL_S });
      }

      // ── everything below requires a verified session
      const sess = await getSession(env, req);

      // ── GET /api/user/profile  (identity comes from the session, never from the query string)
      if (path === "/api/user/profile" && req.method === "GET") {
        if (!sess) return reply(env, req, { error: "UNAUTHORIZED" }, 401);
        const u = await env.FLOODLOCK_KV.get(`user:${sess.uid}`, "json");
        if (!u) return reply(env, req, { error: "UNAUTHORIZED" }, 401);
        const value = await decryptPII(env, u.identity_enc, u.uid);
        return reply(env, req, { user_id: u.uid, identity_masked: maskIdentity({ kind: u.kind, value }), plan: u.plan, daily_quota: PLANS[u.plan].daily_quota });
      }

      // ── POST /api/escrow/payment  (creates a PENDING order; money is not "held" until the gateway confirms)
      if (path === "/api/escrow/payment" && req.method === "POST") {
        if (!sess) return reply(env, req, { error: "UNAUTHORIZED" }, 401);
        const b = await parseJson(req);
        const plan = PLANS[b.plan];
        if (!plan || b.plan === "free") return reply(env, req, { error: "INVALID_PLAN" }, 400);
        if (b.accepted_terms_version !== TERMS_VERSION) return reply(env, req, { error: "TERMS_NOT_ACCEPTED", required_terms_version: TERMS_VERSION }, 400);
        if (!/^[A-Za-z0-9]{12,22}$/.test(String(b.utr || ""))) return reply(env, req, { error: "INVALID_UTR" }, 400);
        const id = `FL_ESCROW_${randomHex(6).toUpperCase()}`;
        const r = await callDO(env.ORDER_LEDGER, id, {
          op: "create",
          order: { id, uid: sess.uid, plan: b.plan, amount_paise: plan.price_paise, utr_ref: b.utr, terms_version: TERMS_VERSION },
        });
        return reply(env, req, {
          order_id: id, status: r.data.order.status, amount_paise: plan.price_paise,
          refund_terms: "Cancel within 5 days of confirmed payment: 50% refunded, 50% retained to cover service costs. Accepted terms version " + TERMS_VERSION + ".",
        }, 201);
      }

      // ── POST /api/escrow/webhook  (payment gateway only; HMAC-signed, replay-limited)
      if (path === "/api/escrow/webhook" && req.method === "POST") {
        const raw = await readBody(req);
        const expected = await hmacHex(env.PAYMENT_WEBHOOK_SECRET, raw);
        if (!safeEqual(expected, req.headers.get("x-signature") || "")) return reply(env, req, { error: "BAD_SIGNATURE" }, 401);
        const e = JSON.parse(raw);
        if (!Number.isFinite(e.ts) || Math.abs(Date.now() - e.ts) > 5 * 60e3) return reply(env, req, { error: "STALE" }, 400);
        if (e.status !== "captured" || !/^FL_ESCROW_[0-9A-F]{12}$/.test(String(e.order_id))) return reply(env, req, { error: "IGNORED" }, 202);
        const r = await callDO(env.ORDER_LEDGER, e.order_id, { op: "confirm", amount_paise: e.amount_paise });
        return reply(env, req, { ok: r.data.ok === true }, r.status);
      }

      // ── POST /api/escrow/refund  (owner only, window enforced, amount computed server-side, idempotent)
      if (path === "/api/escrow/refund" && req.method === "POST") {
        if (!sess) return reply(env, req, { error: "UNAUTHORIZED" }, 401);
        const b = await parseJson(req);
        if (!/^FL_ESCROW_[0-9A-F]{12}$/.test(String(b.order_id))) return reply(env, req, { error: "INVALID_ORDER_ID" }, 400);
        const r = await callDO(env.ORDER_LEDGER, b.order_id, { op: "refund", uid: sess.uid });
        if (r.data.ok && env.REFUND_QUEUE) await env.REFUND_QUEUE.send({ order_id: b.order_id }); // payout happens via the gateway, not here
        return reply(env, req, r.data.ok
          ? { status: r.data.order.status, refund_paise: r.data.order.refund.refund_paise, retained_paise: r.data.order.refund.retained_paise }
          : { error: r.data.reason }, r.status);
      }

      // ── GET /api/escrow/order?id=
      if (path === "/api/escrow/order" && req.method === "GET") {
        if (!sess) return reply(env, req, { error: "UNAUTHORIZED" }, 401);
        const id = url.searchParams.get("id") || "";
        if (!/^FL_ESCROW_[0-9A-F]{12}$/.test(id)) return reply(env, req, { error: "INVALID_ORDER_ID" }, 400);
        const r = await callDO(env.ORDER_LEDGER, id, { op: "get", uid: sess.uid });
        return reply(env, req, r.data.ok ? { order: r.data.order } : { error: r.data.reason }, r.status);
      }

      // ── POST /api/dispatch  (authenticated; provider keys are server-side only)
      if (path === "/api/dispatch" && req.method === "POST") {
        if (!sess) return reply(env, req, { error: "UNAUTHORIZED" }, 401);
        return reply(env, req, await runTacticalReasoning(env, await parseJson(req)));
      }

      return reply(env, req, { error: "NOT_FOUND" }, 404);
    } catch (e) {
      if (e.status) return reply(env, req, { error: e.message.toUpperCase().replace(/\s+/g, "_") }, e.status);
      console.error("UNHANDLED", e); // log server-side, never leak internals
      return reply(env, req, { error: "INTERNAL" }, 500);
    }
  },
};
