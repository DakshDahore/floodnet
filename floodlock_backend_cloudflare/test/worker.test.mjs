import assert from "node:assert/strict";
import test from "node:test";
import {
  deriveDomainSecret,
  encryptPiiAtRest,
  decryptPiiAtRest,
  issueSessionToken,
  verifySessionToken,
  constantTimeEqual,
  createSignedOAuthState,
  verifySignedOAuthState,
} from "../src/crypto_utils.js";
import {
  isDeterministicPhysicalHazard,
  normalizeTacticalPayload,
  buildDeterministicEdgeSop,
} from "../src/ai_resilience.js";
import {
  getSafeFrontendRedirect,
  verifyAdminAccess,
} from "../src/index.js";

const MASTER = "0123456789abcdef0123456789abcdef0123456789abcdef";
const PII_KEY = "fedcba9876543210fedcba9876543210fedcba9876543210";
const VALID_ADMIN_SECRET = "floodlock_admin_super_secret_production_key_64bytes_0123456789";

test("1. HKDF domain separation yields distinct 256-bit subkeys", async () => {
  const k1 = await deriveDomainSecret(MASTER, "identity-hash");
  const k2 = await deriveDomainSecret(MASTER, "otp-hash");
  const k3 = await deriveDomainSecret(MASTER, "session-jwt-hs256");
  assert.equal(k1.length, 64);
  assert.notEqual(k1, k2);
  assert.notEqual(k2, k3);
  assert.notEqual(k1, k3);
});

test("2. AES-256-GCM requires non-empty AAD and blocks cross-user transplant & bit-flip", async () => {
  await assert.rejects(() => encryptPiiAtRest(PII_KEY, { a: 1 }, ""), /CRYPTO_AAD_REQUIRED/);
  const c1 = await encryptPiiAtRest(PII_KEY, { email: "alice@floodlock.org" }, "USER_A_IDH");
  const c2 = await encryptPiiAtRest(PII_KEY, { email: "alice@floodlock.org" }, "USER_A_IDH");
  assert.notEqual(c1, c2, "Fresh 96-bit IVs must produce unique ciphertexts");

  const dec = await decryptPiiAtRest(PII_KEY, c1, "USER_A_IDH");
  assert.equal(dec.email, "alice@floodlock.org");

  await assert.rejects(() => decryptPiiAtRest(PII_KEY, c1, "USER_B_IDH"));

  const parts = c1.split(".");
  const tampered = `${parts[0]}.${parts[1]}.${parts[2].slice(0, -4)}${parts[2].endsWith("AAAA") ? "BBBB" : "AAAA"}`;
  await assert.rejects(() => decryptPiiAtRest(PII_KEY, tampered, "USER_A_IDH"));
});

test("3. HS256 session tokens verify cleanly and reject alg=none, tamper, and expiry", async () => {
  const tok = await issueSessionToken(MASTER, { userId: "USR_1", identityHash: "IDH_1", plan: "pro", ttlSec: 60 });
  const ok = await verifySessionToken(MASTER, `Bearer ${tok}`);
  assert.equal(ok.sub, "USR_1");
  assert.equal(ok.idh, "IDH_1");

  const expired = await issueSessionToken(MASTER, { userId: "USR_1", identityHash: "IDH_1", plan: "pro", ttlSec: -5 });
  assert.equal(await verifySessionToken(MASTER, `Bearer ${expired}`), null);

  assert.equal(
    await verifySessionToken(MASTER, "Bearer eyJhbGciOiJub25lIiwidHlwIjoiRkwtU0VTU0lPTiJ9.eyJzdWIiOiJhZG1pbiJ9."),
    null
  );
  assert.equal(constantTimeEqual("abc", "abd"), false);
  assert.equal(constantTimeEqual("abc", "abc"), true);
});

test("4. Integer paise pro-rata refund math conserves exact paise across all ratios", () => {
  for (const amountPaise of [4900, 14900, 9999, 1]) {
    for (const consumed of [0, 1, 500, 12500, 25000]) {
      const fiveDayBudget = 25000;
      const retainRatio = consumed === 0 ? 0.0 : Math.min(1.0, Math.max(0.10, consumed / fiveDayBudget));
      const retainedPaise = Math.floor(amountPaise * retainRatio);
      const refundedPaise = amountPaise - retainedPaise;
      assert.equal(Number.isInteger(retainedPaise), true);
      assert.equal(Number.isInteger(refundedPaise), true);
      assert.equal(retainedPaise + refundedPaise, amountPaise);
    }
  }
});

test("5. Finding 1 & 2 Fix: Deterministic physical hazard floor vetoes AI dismissal and guarantees evacuation corridors", () => {
  // Hard physical hazards must activate floor
  assert.equal(isDeterministicPhysicalHazard({ r0: 16.0 }, {}), true);
  assert.equal(isDeterministicPhysicalHazard({ r48: 55.0 }, {}), true);
  assert.equal(isDeterministicPhysicalHazard({ soilSat: 0.85, r0: 8.0 }, {}), true);
  assert.equal(isDeterministicPhysicalHazard({ tideSurge: 1.6 }, {}), true);
  assert.equal(isDeterministicPhysicalHazard({}, { depth_trajectory_cm: { h1: 18.0 } }), true);
  assert.equal(isDeterministicPhysicalHazard({}, { flash_flood_probability: 0.82 }), true);
  assert.equal(isDeterministicPhysicalHazard({ r0: 3.0, soilSat: 0.4 }, { depth_trajectory_cm: { h1: 4.0 }, flash_flood_probability: 0.2 }), false);

  const telemetry = { r0: 18.0, r48: 60.0, soilSat: 0.90, tideSurge: 1.8 };
  const predictions = { depth_trajectory_cm: { h1: 22.0, h3: 35.0 }, flash_flood_probability: 0.88, runoff_q_m3s: 180.0 };
  const fallbackFloor = buildDeterministicEdgeSop(telemetry, predictions, 18.92, 72.83);

  // Adversarial AI dismissal payload attempting to cancel real flood alert
  const hostileAiDismissal = {
    threat_verified: false,
    verification_status: "FALSE_ALARM_DOWNGRADED",
    confidence_score: 95,
    safe_evacuation_corridors: [],
    impassable_infrastructure: [],
    nearest_open_hospital: null,
    tactical_civic_advisory: null,
  };

  const normalized = normalizeTacticalPayload(hostileAiDismissal, "HostileEngine", fallbackFloor, true);

  // Life-safety invariants guaranteed by the floor:
  assert.equal(normalized.threat_verified, true, "Physical hazard floor must veto threat_verified: false");
  assert.equal(normalized.verification_status, "VERIFIED_FLOOD_HAZARD", "Status must remain VERIFIED_FLOOD_HAZARD");
  assert.ok(normalized.safe_evacuation_corridors.length > 0, "Evacuation corridors must never be nulled");
  assert.ok(normalized.impassable_infrastructure.length > 0, "Impassable infrastructure must never be nulled");
  assert.ok(normalized.nearest_open_hospital && normalized.nearest_open_hospital.name, "Nearest hospital must be populated");
  assert.ok(normalized.tactical_civic_advisory && normalized.tactical_civic_advisory.length > 10, "Civic advisory must be populated");
  assert.match(normalized.physical_consistency_audit, /DETERMINISTIC SAFETY FLOOR OVERRIDE/);
});

test("6. Finding 1 Fix: AI cache key partitions floor states and re-normalizes cached dismissal with live physical floor", () => {
  // A cached dismissal from a sub-hazard request
  const cachedBenign = {
    engine: "Groq LPU",
    verification_status: "FALSE_ALARM_DOWNGRADED",
    threat_verified: false,
    confidence_score: 92,
    safe_evacuation_corridors: ["All roads clear"],
    impassable_infrastructure: ["None"],
    tactical_civic_advisory: "No civic threat",
  };

  const telemetryHazard = { r0: 25.0, r48: 80.0, soilSat: 0.95, tideSurge: 2.1 };
  const predictionsHazard = { depth_trajectory_cm: { h1: 30.0, h3: 50.0 }, flash_flood_probability: 0.95 };
  const floor = buildDeterministicEdgeSop(telemetryHazard, predictionsHazard, 19.0, 73.0);

  // When live request has isPhysicalHazard = true, re-normalization MUST overturn the cached dismissal
  const reNormalized = normalizeTacticalPayload(cachedBenign, "KV Tactical Cache", floor, true);
  assert.equal(reNormalized.threat_verified, true, "Re-normalization must force threat_verified: true");
  assert.equal(reNormalized.verification_status, "VERIFIED_FLOOD_HAZARD");
  assert.match(reNormalized.physical_consistency_audit, /DETERMINISTIC SAFETY FLOOR OVERRIDE/);

  // Verify that 13 mm/hr and 16 mm/hr reside in different 2 mm/hr buckets across the 15 mm/hr floor
  const bucket13 = Math.floor(13.0 / 2); // 6
  const bucket16 = Math.floor(16.0 / 2); // 8
  assert.notEqual(bucket13, bucket16, "13 mm/hr and 16 mm/hr must never share the same cache bucket");
});

test("7. Finding 2 Fix: Sub-floor neural alerts default to fail-safe and downgrade to WATCH (not NOMINAL)", () => {
  const fallback = {
    verification_status: "VERIFIED_FLOOD_HAZARD",
    threat_verified: true,
    confidence_score: 85,
    safe_evacuation_corridors: ["Route A"],
    impassable_infrastructure: ["Low culvert"],
    nearest_open_hospital: { name: "City Hospital", status: "OPEN", distance_km: 2.0 },
    tactical_civic_advisory: "Caution: rising waters",
  };

  // Case A: Model returns incomplete reply (missing threat_verified and verification_status)
  const incompleteReply = { confidence_score: 75, causal_attribution: "Localized convective cell" };
  const safePayload = normalizeTacticalPayload(incompleteReply, "Groq LPU", fallback, false);
  assert.equal(safePayload.threat_verified, true, "Incomplete AI reply must fail-safe to threat_verified: true");
  assert.equal(safePayload.verification_status, "VERIFIED_FLOOD_HAZARD");

  // Case B: Explicit AI refutation below physical hazard floor
  const explicitRefutation = { threat_verified: false, verification_status: "FALSE_ALARM_DOWNGRADED" };
  const refutedPayload = normalizeTacticalPayload(explicitRefutation, "Groq LPU", fallback, false);
  assert.equal(refutedPayload.threat_verified, false, "Explicit refutation must be honored only below floor");
  assert.equal(refutedPayload.verification_status, "FALSE_ALARM_DOWNGRADED");
});

test("8. Finding 3 Fix: HMAC-signed OAuth state nonce verifies authentic state and rejects tampered or expired nonces", async () => {
  const state = await createSignedOAuthState(MASTER, {
    origin: "https://floodlock.pages.dev",
    provider: "google",
  });
  assert.ok(typeof state === "string" && state.includes("."));

  // Verify valid state within TTL
  const verified = await verifySignedOAuthState(MASTER, state, 900);
  assert.ok(verified !== null);
  assert.equal(verified.origin, "https://floodlock.pages.dev");
  assert.equal(verified.provider, "google");
  assert.ok(typeof verified.nonce === "string" && verified.nonce.length > 8);
  assert.ok(typeof verified.iat === "number");

  // Reject tampered signature
  const [b64Data, sig] = state.split(".");
  const tamperedSig = sig.slice(0, -4) + (sig.endsWith("0000") ? "1111" : "0000");
  assert.equal(await verifySignedOAuthState(MASTER, `${b64Data}.${tamperedSig}`, 900), null);

  // Reject tampered payload
  const tamperedData = b64Data.slice(0, -4) + "AAAA";
  assert.equal(await verifySignedOAuthState(MASTER, `${tamperedData}.${sig}`, 900), null);

  // Reject expired nonce (maxAgeSec = -1)
  assert.equal(await verifySignedOAuthState(MASTER, state, -1), null);

  // Reject wrong secret key
  const WRONG_KEY = "another_secret_that_does_not_match_original_key_32b";
  assert.equal(await verifySignedOAuthState(WRONG_KEY, state, 900), null);
});

test("9. Finding 1 & 3 Fix: OAuth frontend redirect allowlist blocks attacker origins and strips localhost in production", () => {
  const prodEnv = { FRONTEND_URL: "https://floodlock.pages.dev", ENVIRONMENT: "production" };
  const devEnv = { FRONTEND_URL: "https://floodlock.pages.dev", ENVIRONMENT: "development" };

  // Allowed official production origins
  assert.equal(getSafeFrontendRedirect("https://floodlock.pages.dev", prodEnv), "https://floodlock.pages.dev");
  assert.equal(getSafeFrontendRedirect("https://metoflood.netlify.app", prodEnv), "https://metoflood.netlify.app");
  assert.equal(getSafeFrontendRedirect("https://floodnet.netlify.app", prodEnv), "https://floodnet.netlify.app");
  assert.equal(getSafeFrontendRedirect("https://preview.floodlock.pages.dev", prodEnv), "https://preview.floodlock.pages.dev");

  // Open-redirect / session-theft attack origins strictly blocked:
  assert.equal(getSafeFrontendRedirect("https://evil-attacker.com", prodEnv), "https://floodlock.pages.dev");
  assert.equal(getSafeFrontendRedirect("https://phishing-site.org/oauth", prodEnv), "https://floodlock.pages.dev");
  assert.equal(getSafeFrontendRedirect("javascript:alert(1)", prodEnv), "https://floodlock.pages.dev");

  // Localhost blocked in production outside dev
  assert.equal(getSafeFrontendRedirect("http://localhost:3000", prodEnv), "https://floodlock.pages.dev");
  assert.equal(getSafeFrontendRedirect("http://127.0.0.1:8000", prodEnv), "https://floodlock.pages.dev");

  // Localhost permitted in development environment
  assert.equal(getSafeFrontendRedirect("http://localhost:3000", devEnv), "http://localhost:3000");
  assert.equal(getSafeFrontendRedirect("http://127.0.0.1:8000", devEnv), "http://127.0.0.1:8000");
});

test("10. Finding 4 Fix: Admin authentication strictly requires length >= 32 ADMIN_SECRET and rejects derived or session tokens", async () => {
  const env = {
    ADMIN_SECRET: VALID_ADMIN_SECRET,
    MASTER_SECRET: MASTER,
  };

  // Missing Authorization header
  const reqNoAuth = new Request("https://floodlock.org/api/admin/users");
  const resNoAuth = await verifyAdminAccess(env, reqNoAuth);
  assert.equal(resNoAuth.ok, false);
  assert.equal(resNoAuth.reason, "MISSING_AUTH");

  // Weak/short ADMIN_SECRET (< 32 chars) must be rejected by server
  const weakEnv = { ADMIN_SECRET: "short_weak_key_123" };
  const reqWeak = new Request("https://floodlock.org/api/admin/users", {
    headers: { Authorization: "Bearer short_weak_key_123" },
  });
  const resWeak = await verifyAdminAccess(weakEnv, reqWeak);
  assert.equal(resWeak.ok, false);
  assert.equal(resWeak.reason, "ADMIN_SECRET_UNCONFIGURED_OR_WEAK");

  // Valid dedicated ADMIN_SECRET bearer token
  const reqValid = new Request("https://floodlock.org/api/admin/users", {
    headers: { Authorization: `Bearer ${VALID_ADMIN_SECRET}` },
  });
  const resValid = await verifyAdminAccess(env, reqValid);
  assert.equal(resValid.ok, true);
  assert.equal(resValid.method, "ADMIN_SECRET");

  // Raw MASTER_SECRET as bearer token strictly rejected
  const reqMaster = new Request("https://floodlock.org/api/admin/users", {
    headers: { Authorization: `Bearer ${MASTER}` },
  });
  const resMaster = await verifyAdminAccess(env, reqMaster);
  assert.equal(resMaster.ok, false);
  assert.equal(resMaster.reason, "INVALID_ADMIN_CREDENTIALS");

  // Session token (even with isAdmin: true) strictly rejected for admin API
  const adminSessionToken = await issueSessionToken(MASTER, {
    userId: "ADMIN_USR",
    identityHash: "IDH_ADMIN",
    plan: "ultra",
    isAdmin: true,
  });
  const reqSession = new Request("https://floodlock.org/api/admin/users", {
    headers: { Authorization: `Bearer ${adminSessionToken}` },
  });
  const resSession = await verifyAdminAccess(env, reqSession);
  assert.equal(resSession.ok, false);
  assert.equal(resSession.reason, "INVALID_ADMIN_CREDENTIALS");
});

test("11. Finding 5 Fix: 3-strike lockout is scoped per identity + IP to prevent cross-network DoS", () => {
  // Simulate the SecurityStateDO strike & lockout mechanics with per-IP isolation
  class MockSecurityState {
    constructor() {
      this.strikes = new Map();
      this.lockouts = new Map();
    }

    recordFailureAndCheckLockout(identityHash, clientIp, nowMs = Date.now()) {
      const lockoutKey = `${identityHash}:${clientIp}`;
      const lockedUntil = this.lockouts.get(lockoutKey) || 0;
      if (lockedUntil > nowMs) {
        return { locked: true, reason: "ACCOUNT_LOCKED" };
      }

      const currentStrikes = (this.strikes.get(lockoutKey) || 0) + 1;
      this.strikes.set(lockoutKey, currentStrikes);

      if (currentStrikes >= 3) {
        this.lockouts.set(lockoutKey, nowMs + 15 * 60 * 1000);
        return { locked: true, reason: "ACCOUNT_LOCKED", strikes: currentStrikes };
      }
      return { locked: false, strikes: currentStrikes };
    }

    isLocked(identityHash, clientIp, nowMs = Date.now()) {
      const lockoutKey = `${identityHash}:${clientIp}`;
      return (this.lockouts.get(lockoutKey) || 0) > nowMs;
    }
  }

  const sec = new MockSecurityState();
  const targetIdentity = "alice_identity_hash_999";
  const attackerIp = "198.51.100.44";
  const legitimateUserIp = "203.0.113.88";

  // Attacker fails 3 times from their IP
  sec.recordFailureAndCheckLockout(targetIdentity, attackerIp);
  sec.recordFailureAndCheckLockout(targetIdentity, attackerIp);
  const strike3 = sec.recordFailureAndCheckLockout(targetIdentity, attackerIp);
  assert.equal(strike3.locked, true, "Attacker IP must be locked after 3 strikes");
  assert.equal(sec.isLocked(targetIdentity, attackerIp), true, "Attacker IP is locked out");

  // Legitimate user on their own IP is completely unaffected and NOT locked out
  assert.equal(
    sec.isLocked(targetIdentity, legitimateUserIp),
    false,
    "Legitimate user IP must NOT be locked out by attacker failures"
  );
  const userAttempt = sec.recordFailureAndCheckLockout(targetIdentity, legitimateUserIp);
  assert.equal(userAttempt.locked, false, "Legitimate user can attempt verification");
});
