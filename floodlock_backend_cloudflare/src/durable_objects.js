/**
 * cloudflare_worker/src/durable_objects.js
 * ============================================================================
 * Strongly Consistent SQLite-Backed Cloudflare Durable Objects (FloodLock v3.2 Gold)
 * Upgrades Over v3.1:
 *  1. SecurityStateDO:
 *     - Added `rollbackOtp(identityHash)` so failed transactional OTP delivery
 *       (HTTP 502) does NOT poison the 30-second resend cooldown while preserving
 *       rolling 15-minute abuse strikes.
 *     - Added periodic `alarm()` garbage collector pruning expired rate-limit
 *       events, expired OTP challenges, and expired lockouts on idle IPs.
 *  2. BillingStateDO:
 *     - Migrated cleanly to `orders_v3` separating:
 *         * `daily_quota` & `daily_used` (auto-resets every UTC day so Day 2 works!)
 *         * `total_quota_consumed` (monotonic 5-day usage for fair integer-paise
 *           pro-rata refund calculation via `Math.floor`)
 *         * `payout_status` & `gateway_refund_id` updated via `markPayoutResult()`
 *     - Scheduled DO `alarm()` auto-settles expired T+5 holds (`SETTLED`).
 *  3. CircuitBreakerDO:
 *     - Rolling 60-second failure window per AI provider.
 */

import { DurableObject } from "cloudflare:workers";
import { constantTimeEqual } from "./crypto_utils.js";

function utcDayKey(nowMs = Date.now()) {
  return new Date(nowMs).toISOString().slice(0, 10);
}

export class SecurityStateDO extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.ctx = ctx;
    this.sql = ctx.storage.sql;
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS rate_limit_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bucket_key TEXT NOT NULL,
        ts INTEGER NOT NULL
      );
      CREATE INDEX IF NOT EXISTS idx_rle_bucket_ts ON rate_limit_events (bucket_key, ts);

      CREATE TABLE IF NOT EXISTS otp_challenges (
        identity_hash TEXT PRIMARY KEY,
        otp_hash TEXT NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0,
        expires_at INTEGER NOT NULL,
        last_sent_at INTEGER NOT NULL
      );

      CREATE TABLE IF NOT EXISTS otp_strikes (
        identity_hash TEXT PRIMARY KEY,
        strikes INTEGER NOT NULL DEFAULT 0,
        window_start INTEGER NOT NULL
      );

      CREATE TABLE IF NOT EXISTS lockouts (
        identity_hash TEXT PRIMARY KEY,
        locked_until INTEGER NOT NULL
      );
    `);
  }

  async _ensureCleanupAlarm() {
    const existing = await this.ctx.storage.getAlarm();
    if (!existing) {
      await this.ctx.storage.setAlarm(Date.now() + 5 * 60 * 1000);
    }
  }

  /**
   * Periodic SQLite garbage collection so idle IPs/identities do not retain
   * stale rate-limit rows indefinitely.
   */
  async alarm() {
    const now = Date.now();
    // Retain up to 24h for daily demo counters; prune older rows
    this.sql.exec("DELETE FROM rate_limit_events WHERE ts <= ?", now - 86400000);
    this.sql.exec("DELETE FROM otp_challenges WHERE expires_at <= ?", now);
    this.sql.exec("DELETE FROM lockouts WHERE locked_until <= ?", now);
    this.sql.exec("DELETE FROM otp_strikes WHERE window_start <= ?", now - 15 * 60 * 1000);
  }

  /**
   * True sliding-window rate limiter counting exact events in (now - windowMs, now].
   */
  async checkRateLimit(bucketKey, limit = 60, windowMs = 60000) {
    const now = Date.now();
    const cutoff = now - windowMs;
    this.sql.exec("DELETE FROM rate_limit_events WHERE bucket_key = ? AND ts <= ?", bucketKey, cutoff);

    const agg = this.sql
      .exec("SELECT COUNT(*) AS cnt, MIN(ts) AS oldest_ts FROM rate_limit_events WHERE bucket_key = ?", bucketKey)
      .toArray()[0];

    const currentCount = Number(agg?.cnt || 0);
    if (currentCount >= limit) {
      return { allowed: false, remaining: 0, resetAt: Number(agg?.oldest_ts || now) + windowMs };
    }

    this.sql.exec("INSERT INTO rate_limit_events (bucket_key, ts) VALUES (?, ?)", bucketKey, now);
    await this._ensureCleanupAlarm();
    return { allowed: true, remaining: Math.max(0, limit - (currentCount + 1)), resetAt: now + windowMs };
  }

  async issueOtp(identityHash, otpHash, ttlMs = 300000, cooldownMs = 30000) {
    const now = Date.now();
    const lockRow = this.sql
      .exec("SELECT locked_until FROM lockouts WHERE identity_hash = ?", identityHash)
      .toArray()[0];
    if (lockRow && lockRow.locked_until > now) {
      return { ok: false, code: "ACCOUNT_LOCKED", retryAfterSec: Math.ceil((lockRow.locked_until - now) / 1000) };
    }

    const existing = this.sql
      .exec("SELECT last_sent_at, attempts FROM otp_challenges WHERE identity_hash = ?", identityHash)
      .toArray()[0];
    if (existing && now - existing.last_sent_at < cooldownMs) {
      return { ok: false, code: "OTP_COOLDOWN", retryAfterSec: Math.ceil((cooldownMs - (now - existing.last_sent_at)) / 1000) };
    }

    const strikeRow = this.sql
      .exec("SELECT strikes, window_start FROM otp_strikes WHERE identity_hash = ?", identityHash)
      .toArray()[0];
    const rollingStrikes = strikeRow && now - strikeRow.window_start < 15 * 60 * 1000 ? Number(strikeRow.strikes || 0) : 0;
    const prevAttempts = existing && now - existing.last_sent_at < 15 * 60 * 1000 ? Number(existing.attempts || 0) : 0;
    const preservedAttempts = Math.max(rollingStrikes, prevAttempts);

    const expiresAt = now + ttlMs;
    this.sql.exec(
      "INSERT INTO otp_challenges (identity_hash, otp_hash, attempts, expires_at, last_sent_at) " +
        "VALUES (?, ?, ?, ?, ?) " +
        "ON CONFLICT(identity_hash) DO UPDATE SET otp_hash = ?, attempts = ?, expires_at = ?, last_sent_at = ?",
      identityHash, otpHash, preservedAttempts, expiresAt, now,
      otpHash, preservedAttempts, expiresAt, now
    );
    await this._ensureCleanupAlarm();
    return { ok: true, expiresAt };
  }

  /**
   * Rolls back an unsent OTP challenge when the transactional provider fails
   * (HTTP 502) so the user is not trapped in a 30s cooldown for an undelivered code.
   * Rolling strike records remain untouched.
   */
  async rollbackOtp(identityHash) {
    this.sql.exec("DELETE FROM otp_challenges WHERE identity_hash = ?", identityHash);
    return { rolledBack: true };
  }

  _incrementStrikeAndMaybeLock(identityHash, now, currentAttempts = 0) {
    const strikeRow = this.sql
      .exec("SELECT strikes, window_start FROM otp_strikes WHERE identity_hash = ?", identityHash)
      .toArray()[0];
    const rollingStrikes = strikeRow && now - strikeRow.window_start < 15 * 60 * 1000 ? Number(strikeRow.strikes || 0) : 0;
    const nextAttempts = Math.max(rollingStrikes, Number(currentAttempts || 0)) + 1;

    if (nextAttempts >= 3) {
      const lockedUntil = now + 15 * 60 * 1000;
      this.sql.exec(
        "INSERT INTO lockouts (identity_hash, locked_until) VALUES (?, ?) " +
          "ON CONFLICT(identity_hash) DO UPDATE SET locked_until = ?",
        identityHash, lockedUntil, lockedUntil
      );
      this.sql.exec("DELETE FROM otp_challenges WHERE identity_hash = ?", identityHash);
      this.sql.exec("DELETE FROM otp_strikes WHERE identity_hash = ?", identityHash);
      return { locked: true, nextAttempts };
    }

    const windowStart = strikeRow && now - strikeRow.window_start < 15 * 60 * 1000 ? strikeRow.window_start : now;
    this.sql.exec(
      "INSERT INTO otp_strikes (identity_hash, strikes, window_start) VALUES (?, ?, ?) " +
        "ON CONFLICT(identity_hash) DO UPDATE SET strikes = ?, window_start = ?",
      identityHash, nextAttempts, windowStart, nextAttempts, windowStart
    );
    return { locked: false, nextAttempts };
  }

  async verifyOtp(identityHash, submittedHash) {
    const now = Date.now();
    const lockRow = this.sql
      .exec("SELECT locked_until FROM lockouts WHERE identity_hash = ?", identityHash)
      .toArray()[0];
    if (lockRow && lockRow.locked_until > now) {
      return { ok: false, status: 403, code: "ACCOUNT_LOCKED", message: "Too many failed attempts. Identity locked for 15 minutes." };
    }

    const challenge = this.sql
      .exec("SELECT otp_hash, attempts, expires_at FROM otp_challenges WHERE identity_hash = ?", identityHash)
      .toArray()[0];

    if (!challenge || challenge.expires_at <= now) {
      this.sql.exec("DELETE FROM otp_challenges WHERE identity_hash = ?", identityHash);
      const res = this._incrementStrikeAndMaybeLock(identityHash, now, challenge?.attempts || 0);
      if (res.locked) {
        return { ok: false, status: 403, code: "ACCOUNT_LOCKED", message: "3 failed verification attempts. Identity locked for 15 minutes." };
      }
      return { ok: false, status: 400, code: "NO_ACTIVE_OTP", message: "No active OTP request found or code expired." };
    }

    if (constantTimeEqual(challenge.otp_hash, submittedHash)) {
      this.sql.exec("DELETE FROM otp_challenges WHERE identity_hash = ?", identityHash);
      this.sql.exec("DELETE FROM otp_strikes WHERE identity_hash = ?", identityHash);
      this.sql.exec("DELETE FROM lockouts WHERE identity_hash = ?", identityHash);
      return { ok: true };
    }

    const res = this._incrementStrikeAndMaybeLock(identityHash, now, challenge.attempts);
    if (res.locked) {
      return { ok: false, status: 403, code: "ACCOUNT_LOCKED", message: "3 failed verification attempts. Identity locked for 15 minutes." };
    }

    this.sql.exec("UPDATE otp_challenges SET attempts = ? WHERE identity_hash = ?", res.nextAttempts, identityHash);
    return { ok: false, status: 401, code: "INVALID_CODE", message: `Incorrect verification code. ${3 - res.nextAttempts} attempts remaining.` };
  }
}

export class BillingStateDO extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.ctx = ctx;
    this.sql = ctx.storage.sql;
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS orders_v3 (
        order_id TEXT PRIMARY KEY,
        gateway_payment_id TEXT UNIQUE NOT NULL,
        owner_user_id TEXT NOT NULL,
        plan TEXT NOT NULL,
        amount_paise INTEGER NOT NULL,
        daily_quota INTEGER NOT NULL,
        daily_used INTEGER NOT NULL DEFAULT 0,
        daily_window_day TEXT NOT NULL,
        total_quota_consumed INTEGER NOT NULL DEFAULT 0,
        tos_accepted_at TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        refund_window_ends_at INTEGER NOT NULL,
        status TEXT NOT NULL,
        refunded_paise INTEGER NOT NULL DEFAULT 0,
        retained_paise INTEGER NOT NULL DEFAULT 0,
        refund_reason TEXT,
        payout_status TEXT NOT NULL DEFAULT 'NONE',
        gateway_refund_id TEXT
      );
      CREATE INDEX IF NOT EXISTS idx_orders_v3_status_exp ON orders_v3 (status, refund_window_ends_at);
    `);
  }

  async _scheduleNextSettlementAlarm() {
    const nextRow = this.sql
      .exec("SELECT MIN(refund_window_ends_at) AS next_ts FROM orders_v3 WHERE status = 'HOLD_WINDOW_ACTIVE'")
      .toArray()[0];
    if (nextRow && nextRow.next_ts) {
      await this.ctx.storage.setAlarm(Number(nextRow.next_ts));
    }
  }

  async alarm() {
    const now = Date.now();
    this.sql.exec(
      "UPDATE orders_v3 SET status = 'SETTLED' WHERE status = 'HOLD_WINDOW_ACTIVE' AND refund_window_ends_at <= ?",
      now
    );
    await this._scheduleNextSettlementAlarm();
  }

  async createVerifiedOrder(order) {
    const existing = this.sql
      .exec("SELECT * FROM orders_v3 WHERE gateway_payment_id = ?", order.gateway_payment_id)
      .toArray()[0];
    if (existing) return { created: false, order: existing };

    const now = Date.now();
    const today = utcDayKey(now);
    const refundWindowEndsAt = now + 5 * 86400 * 1000;
    const amountPaise = Math.round(Number(order.amount_inr || 0) * 100);

    this.sql.exec(
      `INSERT INTO orders_v3 (
        order_id, gateway_payment_id, owner_user_id, plan, amount_paise,
        daily_quota, daily_used, daily_window_day, total_quota_consumed,
        tos_accepted_at, created_at, refund_window_ends_at, status, payout_status
      ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, 0, ?, ?, ?, 'HOLD_WINDOW_ACTIVE', 'NONE')`,
      order.order_id, order.gateway_payment_id, order.owner_user_id, order.plan,
      amountPaise, order.daily_quota, today, order.tos_accepted_at, now, refundWindowEndsAt
    );
    await this._scheduleNextSettlementAlarm();

    const saved = this.sql.exec("SELECT * FROM orders_v3 WHERE order_id = ?", order.order_id).toArray()[0];
    return { created: true, order: saved };
  }

  /**
   * Enforces true UTC daily rolling quota (resets daily_used when date rolls over)
   * while accumulating total_quota_consumed for fair 5-day pro-rata refund math.
   */
  async consumeQuota(orderId, units = 1) {
    const order = this.sql
      .exec(
        "SELECT daily_quota, daily_used, daily_window_day, total_quota_consumed, status FROM orders_v3 WHERE order_id = ?",
        orderId
      )
      .toArray()[0];

    if (!order || order.status === "REFUNDED") {
      return { allowed: false, reason: "NO_ACTIVE_PLAN" };
    }

    const today = utcDayKey();
    const currentDailyUsed = order.daily_window_day === today ? Number(order.daily_used) : 0;

    if (currentDailyUsed + units > order.daily_quota) {
      return {
        allowed: false,
        reason: "DAILY_QUOTA_EXHAUSTED",
        daily_used: currentDailyUsed,
        daily_quota: order.daily_quota,
        resets_utc_day: today,
      };
    }

    const nextDailyUsed = currentDailyUsed + units;
    const nextTotalConsumed = Number(order.total_quota_consumed) + units;

    this.sql.exec(
      "UPDATE orders_v3 SET daily_used = ?, daily_window_day = ?, total_quota_consumed = ? WHERE order_id = ?",
      nextDailyUsed, today, nextTotalConsumed, orderId
    );

    return {
      allowed: true,
      daily_used: nextDailyUsed,
      daily_remaining: Math.max(0, order.daily_quota - nextDailyUsed),
      total_quota_consumed: nextTotalConsumed,
    };
  }

  /**
   * Processes refund atomically in integer paise via Math.floor against 5-day
   * window budget (daily_quota * 5).
   */
  async processRefund(orderId, requesterUserId, reason, isSlaDefect = false) {
    const order = this.sql.exec("SELECT * FROM orders_v3 WHERE order_id = ?", orderId).toArray()[0];
    if (!order) return { ok: false, status: 404, code: "ORDER_NOT_FOUND", message: "Order does not exist." };
    if (order.owner_user_id !== requesterUserId) return { ok: false, status: 403, code: "FORBIDDEN", message: "Order belongs to another account." };
    if (order.status === "REFUNDED") return { ok: false, status: 409, code: "ALREADY_FINALIZED", message: "Order has already been refunded." };
    if (order.status === "SETTLED") return { ok: false, status: 400, code: "REFUND_WINDOW_EXPIRED", message: "The 5-day refund window has elapsed and funds are settled." };
    if (order.status !== "HOLD_WINDOW_ACTIVE") return { ok: false, status: 409, code: "ALREADY_FINALIZED", message: `Order cannot be refunded from state: ${order.status}` };

    const now = Date.now();
    if (now > order.refund_window_ends_at && !isSlaDefect) {
      this.sql.exec("UPDATE orders_v3 SET status = 'SETTLED' WHERE order_id = ?", orderId);
      return { ok: false, status: 400, code: "REFUND_WINDOW_EXPIRED", message: "The 5-day refund window has elapsed. Order transitioned to SETTLED." };
    }

    const fiveDayQuotaBudget = Math.max(1, Number(order.daily_quota) * 5);
    let retainRatio = 0.0;
    if (!isSlaDefect && order.total_quota_consumed > 0) {
      const usageFraction = Math.min(1.0, order.total_quota_consumed / fiveDayQuotaBudget);
      retainRatio = Math.min(1.0, Math.max(0.10, usageFraction));
    }

    const retainedPaise = Math.floor(order.amount_paise * retainRatio);
    const refundedPaise = order.amount_paise - retainedPaise;
    const initialPayoutStatus = refundedPaise > 0 ? "PENDING_GATEWAY_DISPATCH" : "ZERO_REFUND_DUE";

    this.sql.exec(
      "UPDATE orders_v3 SET status = 'REFUNDED', refunded_paise = ?, retained_paise = ?, refund_reason = ?, payout_status = ? WHERE order_id = ?",
      refundedPaise, retainedPaise, reason, initialPayoutStatus, orderId
    );

    return {
      ok: true,
      refund: {
        order_id: orderId,
        gateway_payment_id: order.gateway_payment_id,
        status: "REFUNDED",
        payout_status: initialPayoutStatus,
        original_amount_inr: order.amount_paise / 100,
        amount_paise: order.amount_paise,
        total_quota_consumed: order.total_quota_consumed,
        five_day_quota_budget: fiveDayQuotaBudget,
        refund_to_customer_inr: refundedPaise / 100,
        refund_paise: refundedPaise,
        retained_metered_compute_inr: retainedPaise / 100,
        retained_paise: retainedPaise,
        policy: "Metered 5-Day Refund Window (100% if unused/SLA defect; integer paise pro-rata against 5-day quota)",
        processed_at: new Date(now).toISOString(),
      },
    };
  }

  async markPayoutResult(orderId, payoutStatus, gatewayRefundId = null) {
    this.sql.exec(
      "UPDATE orders_v3 SET payout_status = ?, gateway_refund_id = ? WHERE order_id = ?",
      payoutStatus, gatewayRefundId, orderId
    );
    return { updated: true, payout_status: payoutStatus, gateway_refund_id: gatewayRefundId };
  }
}

export class CircuitBreakerDO extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec(`
      CREATE TABLE IF NOT EXISTS providers (
        provider TEXT PRIMARY KEY,
        consecutive_failures INTEGER NOT NULL,
        open_until INTEGER NOT NULL,
        last_failure_at INTEGER NOT NULL DEFAULT 0
      );
    `);
    try { this.sql.exec("ALTER TABLE providers ADD COLUMN last_failure_at INTEGER NOT NULL DEFAULT 0;"); } catch {}
  }

  async isOpen(provider) {
    const row = this.sql.exec("SELECT open_until FROM providers WHERE provider = ?", provider).toArray()[0];
    return Boolean(row && row.open_until > Date.now());
  }

  async recordSuccess(provider) {
    this.sql.exec(
      "INSERT INTO providers (provider, consecutive_failures, open_until, last_failure_at) VALUES (?, 0, 0, 0) " +
        "ON CONFLICT(provider) DO UPDATE SET consecutive_failures = 0, open_until = 0, last_failure_at = 0",
      provider
    );
  }

  async recordFailure(provider, threshold = 3, cooldownMs = 60000, windowMs = 60000) {
    const now = Date.now();
    const row = this.sql
      .exec("SELECT consecutive_failures, last_failure_at FROM providers WHERE provider = ?", provider)
      .toArray()[0];
    const failures = row && now - row.last_failure_at < windowMs ? row.consecutive_failures + 1 : 1;
    const openUntil = failures >= threshold ? now + cooldownMs : 0;
    this.sql.exec(
      "INSERT INTO providers (provider, consecutive_failures, open_until, last_failure_at) VALUES (?, ?, ?, ?) " +
        "ON CONFLICT(provider) DO UPDATE SET consecutive_failures = ?, open_until = ?, last_failure_at = ?",
      provider, failures, openUntil, now, failures, openUntil, now
    );
    return { failures, tripped: openUntil > 0 };
  }
}
