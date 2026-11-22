/**
 * cloudflare_worker/src/crypto_utils.js
 * ============================================================================
 * Real WebCrypto Primitives for FloodLock v3.0:
 *  - Constant-time byte comparison
 *  - HMAC-SHA256 signing & verification (WebCrypto)
 *  - Authenticated AES-256-GCM encryption at rest with random 96-bit IVs
 *  - Signed, expirable Bearer Session Tokens (base64url payload + HMAC-SHA256)
 *  - Payment Gateway Webhook HMAC verification (Razorpay / Stripe compatible)
 *  - Strict input validation & PII display masking
 */

const enc = new TextEncoder();
const dec = new TextDecoder();

export function toHex(bytes) {
  return Array.from(new Uint8Array(bytes))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export function fromHex(hex) {
  if (typeof hex !== "string" || hex.length % 2 !== 0) {
    throw new Error("Invalid hex input");
  }
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i++) {
    out[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  }
  return out;
}

export function toBase64Url(bytes) {
  let bin = "";
  const arr = new Uint8Array(bytes);
  for (let i = 0; i < arr.length; i++) bin += String.fromCharCode(arr[i]);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function fromBase64Url(str) {
  const padded = str.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((str.length + 3) % 4);
  const bin = atob(padded);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

export function constantTimeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  const aBytes = enc.encode(a);
  const bBytes = enc.encode(b);
  if (aBytes.length !== bBytes.length) return false;
  let diff = 0;
  for (let i = 0; i < aBytes.length; i++) {
    diff |= aBytes[i] ^ bBytes[i];
  }
  return diff === 0;
}

export async function hmacSha256Hex(secret, message) {
  if (!secret || secret.length < 32) {
    throw new Error("SERVER_MISCONFIGURED: HMAC secret must be >= 32 characters");
  }
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(message));
  return toHex(sig);
}

/**
 * Derives a 256-bit AES-GCM CryptoKey from env.PII_ENCRYPTION_KEY via SHA-256.
 */
async function importAes256Key(keyMaterial) {
  if (!keyMaterial || keyMaterial.length < 32) {
    throw new Error("SERVER_MISCONFIGURED: PII_ENCRYPTION_KEY must be >= 32 characters");
  }
  const digest = await crypto.subtle.digest("SHA-256", enc.encode(keyMaterial));
  return crypto.subtle.importKey("raw", digest, { name: "AES-GCM" }, false, [
    "encrypt",
    "decrypt",
  ]);
}

/**
 * Real AES-256-GCM authenticated encryption at rest with fresh 96-bit IV per write.
 * Returns compact string: "v1.<iv_b64url>.<ciphertext_b64url>"
 */
export async function encryptPiiAtRest(keyMaterial, plaintextObj) {
  const key = await importAes256Key(keyMaterial);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const plaintext = enc.encode(JSON.stringify(plaintextObj));
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    plaintext
  );
  return `v1.${toBase64Url(iv)}.${toBase64Url(ciphertext)}`;
}

export async function decryptPiiAtRest(keyMaterial, token) {
  if (typeof token !== "string" || !token.startsWith("v1.")) {
    throw new Error("Invalid encrypted envelope format");
  }
  const parts = token.split(".");
  if (parts.length !== 3) throw new Error("Malformed encrypted envelope");
  const iv = fromBase64Url(parts[1]);
  const ciphertext = fromBase64Url(parts[2]);
  const key = await importAes256Key(keyMaterial);
  const plainBuf = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv },
    key,
    ciphertext
  );
  return JSON.parse(dec.decode(plainBuf));
}

/**
 * Issues a cryptographically signed Bearer Session Token (HMAC-SHA256).
 * Format: <header_b64url>.<payload_b64url>.<sig_hex>
 */
export async function issueSessionToken(secret, { userId, identityHash, plan, ttlSec = 3600 }) {
  const nowSec = Math.floor(Date.now() / 1000);
  const jti = toHex(crypto.getRandomValues(new Uint8Array(16)));
  const headerB64 = toBase64Url(enc.encode(JSON.stringify({ alg: "HS256", typ: "FL-SESSION" })));
  const payload = {
    sub: userId,
    idh: identityHash,
    plan,
    jti,
    iat: nowSec,
    exp: nowSec + ttlSec,
  };
  const payloadB64 = toBase64Url(enc.encode(JSON.stringify(payload)));
  const signingInput = `${headerB64}.${payloadB64}`;
  const sigHex = await hmacSha256Hex(secret, signingInput);
  return `${signingInput}.${sigHex}`;
}

/**
 * Verifies Bearer Session Token signature, algorithm header, and expiration.
 * Rejects alg=none, tampered payloads, expired tokens, and malformed strings.
 */
export async function verifySessionToken(secret, bearerHeader) {
  if (typeof bearerHeader !== "string" || !bearerHeader.startsWith("Bearer ")) {
    return null;
  }
  const raw = bearerHeader.slice(7).trim();
  if (!raw || raw.length > 2048) return null;

  const parts = raw.split(".");
  if (parts.length !== 3) return null;
  const [headerB64, payloadB64, sigHex] = parts;

  try {
    const header = JSON.parse(dec.decode(fromBase64Url(headerB64)));
    if (header.alg !== "HS256" || header.typ !== "FL-SESSION") return null;

    const expectedSig = await hmacSha256Hex(secret, `${headerB64}.${payloadB64}`);
    if (!constantTimeEqual(expectedSig, sigHex)) return null;

    const payload = JSON.parse(dec.decode(fromBase64Url(payloadB64)));
    const nowSec = Math.floor(Date.now() / 1000);
    if (!payload.sub || !payload.idh || typeof payload.exp !== "number" || payload.exp <= nowSec) {
      return null;
    }
    return payload;
  } catch {
    return null;
  }
}

export function maskIdentity(identity) {
  if (typeof identity !== "string") return "***";
  if (identity.includes("@")) {
    const [local, domain] = identity.split("@");
    const prefix = local.length > 1 ? local[0] : "*";
    return `${prefix}***@${domain}`;
  }
  const digits = identity.replace(/\D/g, "");
  return digits.length >= 4 ? `******${digits.slice(-4)}` : "******";
}

export function isValidIdentity(raw) {
  if (typeof raw !== "string" || raw.length < 5 || raw.length > 120) return false;
  const emailRe = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const phoneRe = /^\+?[1-9]\d{7,14}$/;
  return emailRe.test(raw.trim()) || phoneRe.test(raw.trim());
}

export function sanitizeText(str, maxLen = 256) {
  if (typeof str !== "string") return "";
  return str
    .replace(/[<>'"`;()&$|{}\\]/g, "")
    .replace(/\.\.\//g, "")
    .trim()
    .slice(0, maxLen);
}

export function containsMaliciousPayload(str) {
  if (typeof str !== "string") return false;
  const badPatterns = [
    /<script/i, /javascript:/i, /on\w+\s*=/i, /<iframe/i, /<svg/i, /<img/i,
    /union\s+(all\s+)?select/i, /select\s+.+\s+from/i, /insert\s+into/i,
    /drop\s+table/i, /or\s+['"]?1['"]?\s*=\s*['"]?1/i, /waitfor\s+delay/i,
    /sleep\s*\(/i, /benchmark\s*\(/i, /--/, /\/\*/, /\.\.(\/|\\)/,
    /\/etc\/(passwd|shadow)/i, /\/proc\/self/i, /win\.ini/i,
    /\$\([^)]*\)/, /`[^`]*`/, /;\s*(rm|id|cat|curl|sh|bash|uname)\b/i,
    /\|\s*(uname|sh|bash|cat)\b/i,
  ];
  return badPatterns.some((pat) => pat.test(str));
}
