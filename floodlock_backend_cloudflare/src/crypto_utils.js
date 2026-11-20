/**
 * cloudflare_worker/src/crypto_utils.js
 * ============================================================================
 * Production WebCrypto Primitives for FloodLock v3.2 Gold:
 *  - HKDF-SHA256 cryptographic domain separation (no raw master-key reuse)
 *  - Constant-time byte comparison
 *  - HMAC-SHA256 signing & verification (WebCrypto)
 *  - Authenticated AES-256-GCM encryption at rest with fresh 96-bit random IVs
 *    and MANDATORY Additional Authenticated Data (AAD) binding
 *  - Signed, expirable HS256 Bearer Session Tokens
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

export async function deriveDomainSecret(masterSecret, domainInfo) {
  if (!masterSecret || String(masterSecret).length < 32) {
    throw new Error("SERVER_MISCONFIGURED: masterSecret must be >= 32 characters");
  }
  const baseKey = await crypto.subtle.importKey(
    "raw",
    enc.encode(String(masterSecret)),
    "HKDF",
    false,
    ["deriveBits"]
  );
  const bits = await crypto.subtle.deriveBits(
    {
      name: "HKDF",
      hash: "SHA-256",
      salt: enc.encode("floodlock-v3.2-hkdf-salt"),
      info: enc.encode(`floodlock:${domainInfo}`),
    },
    baseKey,
    256
  );
  return toHex(bits);
}

export async function hmacSha256Hex(secret, message) {
  if (!secret || String(secret).length < 32) {
    throw new Error("SERVER_MISCONFIGURED: HMAC secret must be >= 32 characters");
  }
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(String(secret)),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(String(message)));
  return toHex(sig);
}

async function importAes256Key(keyMaterial) {
  if (!keyMaterial || String(keyMaterial).length < 32) {
    throw new Error("SERVER_MISCONFIGURED: PII_ENCRYPTION_KEY must be >= 32 characters");
  }
  const derivedHex = await deriveDomainSecret(keyMaterial, "aes-256-gcm-pii");
  return crypto.subtle.importKey(
    "raw",
    fromHex(derivedHex),
    { name: "AES-GCM" },
    false,
    ["encrypt", "decrypt"]
  );
}

export async function encryptPiiAtRest(keyMaterial, plaintextObj, aad) {
  if (typeof aad !== "string" || aad.trim().length < 4) {
    throw new Error("CRYPTO_AAD_REQUIRED: Non-empty AAD binding is mandatory");
  }
  const key = await importAes256Key(keyMaterial);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const plaintext = enc.encode(JSON.stringify(plaintextObj));
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv, additionalData: enc.encode(aad) },
    key,
    plaintext
  );
  return `v1.${toBase64Url(iv)}.${toBase64Url(ciphertext)}`;
}

export async function decryptPiiAtRest(keyMaterial, token, aad) {
  if (typeof aad !== "string" || aad.trim().length < 4) {
    throw new Error("CRYPTO_AAD_REQUIRED: Non-empty AAD binding is mandatory");
  }
  if (typeof token !== "string" || !token.startsWith("v1.")) {
    throw new Error("Invalid encrypted envelope format");
  }
  const parts = token.split(".");
  if (parts.length !== 3) throw new Error("Malformed encrypted envelope");
  const iv = fromBase64Url(parts[1]);
  const ciphertext = fromBase64Url(parts[2]);
  const key = await importAes256Key(keyMaterial);
  const plainBuf = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv, additionalData: enc.encode(aad) },
    key,
    ciphertext
  );
  return JSON.parse(dec.decode(plainBuf));
}

export async function issueSessionToken(masterSecret, { userId, identityHash, plan, isAdmin = false, ttlSec = 3600 }) {
  const sessionKey = await deriveDomainSecret(masterSecret, "session-jwt-hs256");
  const nowSec = Math.floor(Date.now() / 1000);
  const jti = toHex(crypto.getRandomValues(new Uint8Array(16)));
  const headerB64 = toBase64Url(enc.encode(JSON.stringify({ alg: "HS256", typ: "FL-SESSION" })));
  const payload = { sub: userId, idh: identityHash, plan, isAdmin: Boolean(isAdmin), jti, iat: nowSec, exp: nowSec + ttlSec };
  const payloadB64 = toBase64Url(enc.encode(JSON.stringify(payload)));
  const signingInput = `${headerB64}.${payloadB64}`;
  const sigHex = await hmacSha256Hex(sessionKey, signingInput);
  return `${signingInput}.${sigHex}`;
}

export async function verifySessionToken(masterSecret, bearerHeader) {
  if (typeof bearerHeader !== "string" || !bearerHeader.startsWith("Bearer ")) return null;
  const raw = bearerHeader.slice(7).trim();
  if (!raw || raw.length > 2048) return null;
  const parts = raw.split(".");
  if (parts.length !== 3) return null;
  const [headerB64, payloadB64, sigHex] = parts;

  try {
    const header = JSON.parse(dec.decode(fromBase64Url(headerB64)));
    if (header.alg !== "HS256" || header.typ !== "FL-SESSION") return null;

    const sessionKey = await deriveDomainSecret(masterSecret, "session-jwt-hs256");
    const expectedSig = await hmacSha256Hex(sessionKey, `${headerB64}.${payloadB64}`);
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
  return str.replace(/[<>'"`;()&$|{}\\]/g, "").replace(/\.\.\//g, "").trim().slice(0, maxLen);
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
