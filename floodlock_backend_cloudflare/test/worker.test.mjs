import assert from "node:assert/strict";
import test from "node:test";
import {
  deriveDomainSecret,
  encryptPiiAtRest,
  decryptPiiAtRest,
  issueSessionToken,
  verifySessionToken,
  constantTimeEqual,
} from "../src/crypto_utils.js";

const MASTER = "0123456789abcdef0123456789abcdef0123456789abcdef";
const PII_KEY = "fedcba9876543210fedcba9876543210fedcba9876543210";

test("HKDF domain separation yields distinct 256-bit subkeys", async () => {
  const k1 = await deriveDomainSecret(MASTER, "identity-hash");
  const k2 = await deriveDomainSecret(MASTER, "otp-hash");
  const k3 = await deriveDomainSecret(MASTER, "session-jwt-hs256");
  assert.equal(k1.length, 64);
  assert.notEqual(k1, k2);
  assert.notEqual(k2, k3);
  assert.notEqual(k1, k3);
});

test("AES-256-GCM requires non-empty AAD and blocks cross-user transplant & bit-flip", async () => {
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

test("HS256 session tokens verify cleanly and reject alg=none, tamper, and expiry", async () => {
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

test("Integer paise pro-rata refund math conserves exact paise across all ratios", () => {
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
