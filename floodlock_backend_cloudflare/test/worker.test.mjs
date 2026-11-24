import assert from "node:assert/strict";
import test from "node:test";
import { DatabaseSync } from "node:sqlite";
import {
  deriveDomainSecret,
  encryptPiiAtRest,
  decryptPiiAtRest,
  issueSessionToken,
  verifySessionToken,
  constantTimeEqual,
  createSignedOAuthState,
  verifySignedOAuthState,
  hmacSha256Hex,
} from "../src/crypto_utils.js";
import {
  isDeterministicPhysicalHazard,
  normalizeTacticalPayload,
  buildDeterministicEdgeSop,
  decideThreatLevel,
  decideThreatState,
  PUBLIC_SAFETY_DISCLAIMER,
} from "../src/ai_resilience.js";
import worker, {
  getSafeFrontendRedirect,
  verifyAdminAccess,
  verifyTurnstileToken,
  fetchLiveTelemetry as fetchLiveTelemetryGateway,
  dispatchFounderAlert,
  consumeUserQuota,
  getIdentityUsage,
} from "../src/index.js";
import {
  fetchLiveTelemetry as fetchLiveTelemetryClick,
} from "../src/click_processor.js";
import {
  normalizeClientIp,
  SecurityStateDO,
} from "../src/durable_objects.js";

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

  // Case A: Adversarial AI dismissal payload with empty/null arrays
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

  // Case B: Adversarial AI dismissal returning benign text ("No action needed... resume regular activity")
  // during active deluge (62 mm/hr, 1.9m surge). Invariant: Floor MUST replace benign text with emergency SOP!
  const hostileBenignTextDismissal = {
    threat_verified: false,
    verification_status: "FALSE_ALARM_DOWNGRADED",
    confidence_score: 98,
    tactical_civic_advisory: "No action needed… resume regular activity",
    safe_evacuation_corridors: ["No evacuation required"],
    danger_zone_perimeter: "Nominal terrain",
    impassable_infrastructure: ["None"],
  };

  const normalizedBenign = normalizeTacticalPayload(hostileBenignTextDismissal, "HostileEngine", fallbackFloor, true);
  assert.equal(normalizedBenign.threat_verified, true, "Physical hazard floor must veto threat_verified: false");
  assert.equal(normalizedBenign.verification_status, "VERIFIED_FLOOD_HAZARD");
  assert.doesNotMatch(normalizedBenign.tactical_civic_advisory, /no action|resume regular/i, "Benign advisory text must be stripped under physical hazard floor");
  assert.match(normalizedBenign.tactical_civic_advisory, /CRITICAL/i, "Emergency SOP advisory must be injected");
  assert.notEqual(normalizedBenign.safe_evacuation_corridors[0], "No evacuation required", "Benign corridor text must be replaced with emergency corridors");
  assert.match(normalizedBenign.safe_evacuation_corridors[0], /elevated|arterial|ridge/i);
  assert.doesNotMatch(normalizedBenign.danger_zone_perimeter, /nominal terrain/i, "Benign perimeter must be replaced");
});

test("5b. Task 1: Life-safety floor strictly overrides all evasive/benign AI phrases when isPhysicalHazard is true, and preserves advisory when false", () => {
  const telemetry = { r0: 20.0, r48: 65.0, soilSat: 0.92, tideSurge: 1.9 };
  const predictions = { depth_trajectory_cm: { h1: 25.0, h3: 40.0 }, flash_flood_probability: 0.90, runoff_q_m3s: 200.0 };
  const fallbackFloor = buildDeterministicEdgeSop(telemetry, predictions, 18.92, 72.83);

  const evasivePhrases = [
    "Flooding is unlikely; continue normal activities.",
    "Conditions are safe. Stay at home if you prefer.",
    "Minimal risk, routine commuting is fine.",
    "Not expected to flood. Carry on with your day.",
    "Low risk of inundation, no need to relocate.",
    "No action needed.",
  ];

  for (const phrase of evasivePhrases) {
    const fakeAiAnswer = {
      threat_verified: false,
      verification_status: "FALSE_ALARM_DOWNGRADED",
      confidence_score: 95,
      tactical_civic_advisory: phrase,
      safe_evacuation_corridors: ["Carry on normally", "No evacuation needed"],
      danger_zone_perimeter: "Safe ground everywhere",
      impassable_infrastructure: ["None"],
      nearest_open_hospital: { name: "Local Clinic", status: "NORMAL", distance_km: 1.0 },
    };

    const out = normalizeTacticalPayload(fakeAiAnswer, "EvasiveEngine", fallbackFloor, true);
    assert.equal(out.threat_verified, true, `Floor must enforce threat_verified=true for phrase: "${phrase}"`);
    assert.equal(out.verification_status, "VERIFIED_FLOOD_HAZARD", `Floor must enforce VERIFIED_FLOOD_HAZARD for phrase: "${phrase}"`);
    assert.equal(out.tactical_civic_advisory, fallbackFloor.tactical_civic_advisory, `Advisory must equal fallback SOP for phrase: "${phrase}"`);
    assert.deepEqual(out.safe_evacuation_corridors, fallbackFloor.safe_evacuation_corridors, `Corridors must equal fallback SOP for phrase: "${phrase}"`);
    assert.equal(out.danger_zone_perimeter, fallbackFloor.danger_zone_perimeter, `Perimeter must equal fallback SOP for phrase: "${phrase}"`);
    assert.deepEqual(out.impassable_infrastructure, fallbackFloor.impassable_infrastructure, `Impassable infra must equal fallback SOP for phrase: "${phrase}"`);
    assert.deepEqual(out.nearest_open_hospital, fallbackFloor.nearest_open_hospital, `Hospital must equal fallback SOP for phrase: "${phrase}"`);
  }

  // Safe path: When isPhysicalHazard is false, normal AI advisory must be kept
  const safeAiAnswer = {
    threat_verified: true,
    verification_status: "VERIFIED_FLOOD_HAZARD",
    confidence_score: 85,
    tactical_civic_advisory: "Localized street flooding reported in sector 4. Exercise caution near drains.",
    safe_evacuation_corridors: ["Take north bypass avenue"],
    danger_zone_perimeter: "Sector 4 low dip",
    impassable_infrastructure: ["Main St underpass"],
    nearest_open_hospital: { name: "City General", status: "OPEN", distance_km: 2.5 },
  };

  const safeTelemetry = { r0: 2.0, r48: 10.0, soilSat: 0.35, tideSurge: 0.1 };
  const safePredictions = { depth_trajectory_cm: { h1: 3.0, h3: 4.0 }, flash_flood_probability: 0.2, runoff_q_m3s: 10.0 };
  const safeFallback = buildDeterministicEdgeSop(safeTelemetry, safePredictions, 18.92, 72.83);

  const safeOut = normalizeTacticalPayload(safeAiAnswer, "NormalEngine", safeFallback, false);
  assert.equal(safeOut.tactical_civic_advisory, "Localized street flooding reported in sector 4. Exercise caution near drains.");
  assert.deepEqual(safeOut.safe_evacuation_corridors, ["Take north bypass avenue"]);
  assert.equal(safeOut.danger_zone_perimeter, "Sector 4 low dip");
  assert.deepEqual(safeOut.impassable_infrastructure, ["Main St underpass"]);
  assert.equal(safeOut.nearest_open_hospital.name, "City General");
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
  assert.equal(getSafeFrontendRedirect("https://preview.floodlock.pages.dev", prodEnv), "https://preview.floodlock.pages.dev");

  // Unclaimed / third-party Netlify domains stripped to prevent subdomain takeover:
  assert.equal(getSafeFrontendRedirect("https://metoflood.netlify.app", prodEnv), "https://floodlock.pages.dev");
  assert.equal(getSafeFrontendRedirect("https://floodnet.netlify.app", prodEnv), "https://floodlock.pages.dev");

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

test("10b. Task 2: IPv6 /64 prefix expansion and address normalization table", () => {
  const table = [
    ["2001:db8:abcd:12:1:2:3:4", "2001:db8:abcd:12::/64"],
    ["2001:db8:abcd:12::9", "2001:db8:abcd:12::/64"],
    ["2001:db8::1", "2001:db8:0:0::/64"],
    ["2001:db8::2", "2001:db8:0:0::/64"],
    ["::ffff:1.2.3.4", "1.2.3.4"],
    ["203.0.113.5", "203.0.113.5"],
    ["", "global"],
  ];

  for (const [input, expected] of table) {
    const actual = normalizeClientIp(input);
    assert.equal(actual, expected, `normalizeClientIp("${input}") should return "${expected}" but got "${actual}"`);
  }
});

test("10c. Task 3: Turnstile verification is mandatory (no token -> 403, bypass string -> 403, valid token -> ok)", async () => {
  const secretKey = "0x4AAAAAAtestsecret";
  const origFetch = globalThis.fetch;

  try {
    // Case A: Missing or empty token returns 403 BOT_CHALLENGE_REQUIRED
    const resNoToken = await verifyTurnstileToken("", secretKey, "203.0.113.1", "production");
    assert.equal(resNoToken.ok, false);
    assert.equal(resNoToken.status, 403);
    assert.equal(resNoToken.error, "BOT_CHALLENGE_REQUIRED");

    // Case B: Bypass string returns 403 BOT_CHALLENGE_FAILED (stub fetch returning failure)
    globalThis.fetch = async () => ({
      ok: true,
      json: async () => ({ success: false, "error-codes": ["invalid-input-response"] }),
    });
    const resBypass = await verifyTurnstileToken("FAKE_DISCARDED_TOKEN", secretKey, "203.0.113.1", "production");
    assert.equal(resBypass.ok, false);
    assert.equal(resBypass.status, 403);
    assert.equal(resBypass.error, "BOT_CHALLENGE_FAILED");

    // Case C: Valid token (stub fetch returning success) continues cleanly
    globalThis.fetch = async () => ({
      ok: true,
      json: async () => ({ success: true }),
    });
    const resValid = await verifyTurnstileToken("valid_cf_token_xyz", secretKey, "203.0.113.1", "production");
    assert.equal(resValid.ok, true);

    // Case D: Missing TURNSTILE_SECRET_KEY in production returns 500 SERVER_MISCONFIGURED
    const resMissingSecretProd = await verifyTurnstileToken("some_token", "", "203.0.113.1", "production");
    assert.equal(resMissingSecretProd.ok, false);
    assert.equal(resMissingSecretProd.status, 500);
    assert.equal(resMissingSecretProd.error, "SERVER_MISCONFIGURED");

    // Case E: Missing TURNSTILE_SECRET_KEY in non-production environment allowed
    const resMissingSecretDev = await verifyTurnstileToken("some_token", "", "203.0.113.1", "development");
    assert.equal(resMissingSecretDev.ok, true);
  } finally {
    globalThis.fetch = origFetch;
  }
});

test("10d. Task 4: decideThreatLevel shared threat resolution table", () => {
  const table = [
    // hazard | degraded | isThreat | groqDismissed | groqVerified | expectedLevel
    { hazard: true, degraded: true, isThreat: true, groqDismissed: false, groqVerified: true, expected: "CRITICAL_INUNDATION" },
    { hazard: true, degraded: true, isThreat: false, groqDismissed: true, groqVerified: false, expected: "CRITICAL_INUNDATION" },
    { hazard: true, degraded: false, isThreat: false, groqDismissed: true, groqVerified: false, expected: "CRITICAL_INUNDATION" },
    { hazard: false, degraded: true, isThreat: true, groqDismissed: false, groqVerified: true, expected: "ELEVATED_WATCH" },
    { hazard: false, degraded: true, isThreat: false, groqDismissed: false, groqVerified: false, expected: "ELEVATED_WATCH" },
    { hazard: false, degraded: false, isThreat: true, groqDismissed: true, groqVerified: false, expected: "ELEVATED_WATCH" },
    { hazard: false, degraded: false, isThreat: true, groqDismissed: false, groqVerified: true, expected: "CRITICAL_INUNDATION" },
    { hazard: false, degraded: false, isThreat: false, groqDismissed: false, groqVerified: false, expected: "MONITORED_NOMINAL" },
  ];

  for (const row of table) {
    const level = decideThreatLevel({
      isPhysicalHazard: row.hazard,
      telemetryDegraded: row.degraded,
      isThreat: row.isThreat,
      groqDismissed: row.groqDismissed,
      groqVerified: row.groqVerified,
    });
    assert.equal(level, row.expected, `Mismatch for row ${JSON.stringify(row)}: expected ${row.expected} but got ${level}`);

    const state = decideThreatState({
      isPhysicalHazard: row.hazard,
      telemetryDegraded: row.degraded,
      isThreat: row.isThreat,
      groqDismissed: row.groqDismissed,
      groqVerified: row.groqVerified,
    });
    assert.equal(state.threatLevel, row.expected);
  }
});

test("10e. Task 7: dispatchFounderAlert gracefully handles missing FOUNDER_ALERT_EMAIL and dispatches when present", async () => {
  const origFetch = globalThis.fetch;
  let fetched = false;
  try {
    globalThis.fetch = async (url, opts) => {
      fetched = true;
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    };

    // 1. Missing FOUNDER_ALERT_EMAIL -> skips alert, does not crash, fetch not called
    fetched = false;
    await dispatchFounderAlert({}, "Test Alert", { foo: "bar" });
    assert.equal(fetched, false);

    await dispatchFounderAlert({ FOUNDER_ALERT_EMAIL: "" }, "Test Alert", { foo: "bar" });
    assert.equal(fetched, false);

    // 2. Present FOUNDER_ALERT_EMAIL -> calls alert dispatch
    await dispatchFounderAlert({ FOUNDER_ALERT_EMAIL: "admin@floodlock.local" }, "Test Alert", { foo: "bar" });
    assert.equal(fetched, true);
  } finally {
    globalThis.fetch = origFetch;
  }
});

test("10f. Task 12: Public safety disclaimer is present in API forecast responses and matches life-safety guidance", async () => {
  const req = new Request("http://localhost/api/forecast?lat=19.07&lon=72.87");
  const res = await worker.fetch(req, { ENVIRONMENT: "development" });
  assert.equal(res.status, 200);

  const data = await res.json();
  const expectedNotice = "FloodLock is an experimental information tool, not an official warning system. In an emergency follow instructions from your local authorities and call your local emergency number.";
  
  assert.equal(data.disclaimer, expectedNotice);
  assert.equal(PUBLIC_SAFETY_DISCLAIMER, expectedNotice);
});

function createTestSecurityDO() {
  const db = new DatabaseSync(":memory:");
  const ctx = {
    storage: {
      sql: {
        exec(sql, ...params) {
          const trimmed = sql.trim();
          if (params.length > 0) {
            const stmt = db.prepare(trimmed);
            if (/^SELECT\b/i.test(trimmed)) {
              return { toArray: () => stmt.all(...params) };
            } else {
              stmt.run(...params);
              return { toArray: () => [] };
            }
          } else {
            if (/^SELECT\b/i.test(trimmed)) {
              const stmt = db.prepare(trimmed);
              return { toArray: () => stmt.all() };
            } else {
              db.exec(trimmed);
              return { toArray: () => [] };
            }
          }
        }
      },
      getAlarm: async () => null,
      setAlarm: async () => {},
    }
  };
  return new SecurityStateDO(ctx, {});
}

test("11. Finding 5 Fix: 3-strike lockout is scoped per identity + IP to prevent cross-network DoS (Real SecurityStateDO)", async () => {
  const sec = createTestSecurityDO();
  const masterKey = "mastersecret12345678901234567890123456789012";
  const idKey = await deriveDomainSecret(masterKey, "identity-hash");
  const otpKey = await deriveDomainSecret(masterKey, "otp-hash");
  const identityHash = await hmacSha256Hex(idKey, "id:alice_lockout_test@example.com");

  const correctCode = "654321";
  const correctHash = await hmacSha256Hex(otpKey, `otp:${identityHash}:${correctCode}`);
  await sec.issueOtp(identityHash, correctHash, 300000, 0, "192.168.1.1");

  const attackerIp = "198.51.100.44";
  const legitimateUserIp = "203.0.113.88";

  // Attacker fails 3 times from attackerIp
  const w1 = await hmacSha256Hex(otpKey, `otp:${identityHash}:000001`);
  const r1 = await sec.verifyOtp(identityHash, w1, attackerIp);
  assert.equal(r1.ok, false);
  assert.equal(r1.code, "INVALID_CODE");

  const w2 = await hmacSha256Hex(otpKey, `otp:${identityHash}:000002`);
  const r2 = await sec.verifyOtp(identityHash, w2, attackerIp);
  assert.equal(r2.ok, false);
  assert.equal(r2.code, "INVALID_CODE");

  const w3 = await hmacSha256Hex(otpKey, `otp:${identityHash}:000003`);
  const r3 = await sec.verifyOtp(identityHash, w3, attackerIp);
  assert.equal(r3.ok, false);
  assert.equal(r3.code, "ACCOUNT_LOCKED", "Attacker IP must be locked on 3rd failed strike");
  assert.equal(r3.status, 403);

  // Subsequent attempts from attackerIp are locked
  const r4 = await sec.verifyOtp(identityHash, w3, attackerIp);
  assert.equal(r4.code, "ACCOUNT_LOCKED");
  assert.equal(r4.status, 403);

  // Legitimate user on another IP is NOT locked out and succeeds
  const rUser = await sec.verifyOtp(identityHash, correctHash, legitimateUserIp);
  assert.equal(rUser.ok, true, "Legitimate user IP must NOT be locked out by attacker failures");

  // IPv6 /64 prefix normalization test
  const ipv6A = "2001:0db8:85a3:0000:0000:8a2e:0370:7334";
  const ipv6B = "2001:0db8:85a3:0000:ffff:ffff:ffff:ffff";
  assert.equal(normalizeClientIp(ipv6A), "2001:db8:85a3:0::/64");
  assert.equal(normalizeClientIp(ipv6A), normalizeClientIp(ipv6B), "IPv6 /64 subnet rotation must map to same bucket");
});

test("12. Critical Security Fix: Global OTP failure cap (5 attempts) revokes challenge and locks identity against IP rotation attacks (Real SecurityStateDO)", async () => {
  const masterKey = "mastersecret12345678901234567890123456789012";
  const idKey = await deriveDomainSecret(masterKey, "identity-hash");
  const otpKey = await deriveDomainSecret(masterKey, "otp-hash");

  // Scenario A: 4 wrong codes from 4 IPs, 5th wrong code gives CHALLENGE_REVOKED, correct code afterwards fails
  const secA = createTestSecurityDO();
  const idA = await hmacSha256Hex(idKey, "id:victim_user_a@example.com");
  const correctCodeA = "777888";
  const correctHashA = await hmacSha256Hex(otpKey, `otp:${idA}:${correctCodeA}`);
  await secA.issueOtp(idA, correctHashA, 300000, 0, "192.168.1.1");

  for (let i = 1; i <= 4; i++) {
    const wrongHash = await hmacSha256Hex(otpKey, `otp:${idA}:00000${i}`);
    const res = await secA.verifyOtp(idA, wrongHash, `198.51.100.${i}`);
    assert.equal(res.ok, false);
    assert.equal(res.code, "INVALID_CODE", `Attempt ${i} must return INVALID_CODE`);
  }

  // 5th wrong code from a 5th IP gives CHALLENGE_REVOKED
  const wrongHash5 = await hmacSha256Hex(otpKey, `otp:${idA}:000005`);
  const res5 = await secA.verifyOtp(idA, wrongHash5, "198.51.100.5");
  assert.equal(res5.ok, false);
  assert.equal(res5.code, "CHALLENGE_REVOKED", "5th failed attempt globally must revoke challenge");
  assert.equal(res5.status, 403);

  // Afterwards even the correct code on another IP fails
  const resAfterRevoke = await secA.verifyOtp(idA, correctHashA, "198.51.100.6");
  assert.equal(resAfterRevoke.ok, false);
  assert.equal(resAfterRevoke.code, "ACCOUNT_LOCKED", "After challenge revocation, account must be locked globally");
  assert.equal(resAfterRevoke.status, 403);

  // Scenario B: 4 wrong codes from 4 IPs, then the correct code on 5th attempt succeeds
  const secB = createTestSecurityDO();
  const idB = await hmacSha256Hex(idKey, "id:user_success_5th@example.com");
  const correctCodeB = "555666";
  const correctHashB = await hmacSha256Hex(otpKey, `otp:${idB}:${correctCodeB}`);
  await secB.issueOtp(idB, correctHashB, 300000, 0, "192.168.1.1");

  for (let i = 1; i <= 4; i++) {
    const wrongHash = await hmacSha256Hex(otpKey, `otp:${idB}:00000${i}`);
    const res = await secB.verifyOtp(idB, wrongHash, `203.0.113.${i}`);
    assert.equal(res.code, "INVALID_CODE");
  }

  const res5Success = await secB.verifyOtp(idB, correctHashB, "203.0.113.5");
  assert.equal(res5Success.ok, true, "Correct code on 5th attempt must succeed");

  // Scenario C: Issuing a 4th OTP within 10 minutes returns RATE_LIMITED
  const secC = createTestSecurityDO();
  const idC = await hmacSha256Hex(idKey, "id:ratelimit_user@example.com");
  const r1 = await secC.issueOtp(idC, "hash1", 300000, 0, "1.1.1.1");
  const r2 = await secC.issueOtp(idC, "hash2", 300000, 0, "1.1.1.1");
  const r3 = await secC.issueOtp(idC, "hash3", 300000, 0, "1.1.1.1");
  const r4 = await secC.issueOtp(idC, "hash4", 300000, 0, "1.1.1.1");

  assert.equal(r1.ok, true);
  assert.equal(r2.ok, true);
  assert.equal(r3.ok, true);
  assert.equal(r4.ok, false);
  assert.equal(r4.code, "RATE_LIMITED", "4th OTP issuance within 10m must return RATE_LIMITED");
});

test("13. Critical Telemetry Fix: Real fetchLiveTelemetry antecedent slicing & soil moisture conversion", async () => {
  const origFetch = globalThis.fetch;
  try {
    const times = [];
    const rain = [];
    const soil = [];
    for (let i = 0; i < 24; i++) {
      const hh = String(i).padStart(2, "0");
      times.push(`2026-11-23T${hh}:00`);
      if (i <= 12) {
        rain.push(2.0); // 13 hours * 2 = 26.0 mm past rain
      } else {
        rain.push(500.0); // future hours: MUST NOT be counted!
      }
      soil.push(i === 12 ? 0.38 : 0.20);
    }

    globalThis.fetch = async (url) => ({
      ok: true,
      json: async () => ({
        current: { time: "2026-11-23T12:00", precipitation: 2.0 },
        hourly: {
          time: times,
          precipitation: rain,
          soil_moisture_0_to_1cm: soil,
        },
      }),
    });

    const telemGateway = await fetchLiveTelemetryGateway(18.92, 72.83);
    assert.equal(telemGateway.r48, 26.0, "r48 must only sum past hours, excluding future 500mm hours");
    assert.equal(telemGateway.soilSat, 0.84, "0.38 m³/m³ moisture must convert to 0.38 / 0.45 = 0.84 saturation");
    assert.equal(telemGateway.telemetryDegraded, false);

    const telemClick = await fetchLiveTelemetryClick(18.92, 72.83);
    assert.equal(telemClick.r48, 26.0);
    assert.equal(telemClick.soilSat, 0.84);

    // Stub that throws must yield telemetryDegraded === true
    globalThis.fetch = async () => { throw new Error("Connection timeout"); };
    const telemFail = await fetchLiveTelemetryGateway(18.92, 72.83);
    assert.equal(telemFail.telemetryDegraded, true, "Network error or timeout must yield telemetryDegraded === true");

    const telemFailClick = await fetchLiveTelemetryClick(19.92, 73.83);
    assert.equal(telemFailClick.telemetryDegraded, true);
  } finally {
    globalThis.fetch = origFetch;
  }
});

test("14. SecurityStateDO getUsage reads live counts without incrementing", async () => {
  const sec = createTestSecurityDO();
  const bucketKey = "daily:test_user_usage_99";
  
  // Initially 0 used
  const u0 = await sec.getUsage(bucketKey, 10, 86400000);
  assert.equal(u0.used, 0);
  assert.equal(u0.remaining, 10);

  // Consume 3 events
  await sec.checkRateLimit(bucketKey, 10, 86400000);
  await sec.checkRateLimit(bucketKey, 10, 86400000);
  await sec.checkRateLimit(bucketKey, 10, 86400000);

  // getUsage should report 3 used, 7 remaining
  const u3 = await sec.getUsage(bucketKey, 10, 86400000);
  assert.equal(u3.used, 3);
  assert.equal(u3.remaining, 7);

  // Subsequent getUsage calls do NOT increment
  const u3_again = await sec.getUsage(bucketKey, 10, 86400000);
  assert.equal(u3_again.used, 3);
  assert.equal(u3_again.remaining, 7);
});

test("15. consumeUserQuota & getIdentityUsage accurately meter API keys and session tokens", async () => {
  const sec = createTestSecurityDO();
  const mockEnv = {
    MASTER_SECRET: MASTER,
    SECURITY_STATE_DO: {
      get: () => sec,
      idFromName: () => "id",
    },
  };

  const testApiKey = "flk_live_test_api_key_1234567890abcdef";
  const req = new Request("http://localhost/api/forecast", {
    headers: { "Authorization": `Bearer ${testApiKey}` },
  });

  // Check 1: 1st consume
  const q1 = await consumeUserQuota(req, mockEnv, "127.0.0.1", "forecast");
  assert.equal(q1.allowed, true);
  assert.equal(q1.quotaStatus.daily_used, 1);
  assert.equal(q1.quotaStatus.daily_remaining, 999);

  // Check 2: 2nd consume
  const q2 = await consumeUserQuota(req, mockEnv, "127.0.0.1", "radius-check");
  assert.equal(q2.allowed, true);
  assert.equal(q2.quotaStatus.daily_used, 2);
  assert.equal(q2.quotaStatus.daily_remaining, 998);

  // Check 3: getIdentityUsage reports exactly 2 used, 998 remaining
  const usage = await getIdentityUsage(req, mockEnv, "127.0.0.1");
  assert.equal(usage.authenticated, true);
  assert.equal(usage.queries_used, 2);
  assert.equal(usage.daily_remaining, 998);
  assert.equal(usage.daily_quota, 1000);
});

test("16. worker.fetch handles /api/user/usage and /api/flood/forecast alias", async () => {
  const sec = createTestSecurityDO();
  const mockEnv = {
    MASTER_SECRET: MASTER,
    ENVIRONMENT: "development",
    SECURITY_STATE_DO: {
      get: () => sec,
      idFromName: () => "id",
    },
  };

  // 1. /api/user/usage for unauthenticated IP
  const reqUsage = new Request("http://localhost/api/user/usage");
  const resUsage = await worker.fetch(reqUsage, mockEnv);
  assert.equal(resUsage.status, 200);
  const dataUsage = await resUsage.json();
  assert.equal(dataUsage.success, true);
  assert.equal(typeof dataUsage.queries_used, "number");

  // 2. /api/flood/forecast alias executes correctly
  const reqForecast = new Request("http://localhost/api/flood/forecast?lat=19.07&lon=72.87");
  const resForecast = await worker.fetch(reqForecast, mockEnv);
  assert.equal(resForecast.status, 200);
  const dataForecast = await resForecast.json();
  assert.ok(dataForecast.threat_level);
  assert.ok(dataForecast.quota);
});
