// crypto.js - all secrets come from env (wrangler secrets). Nothing is hardcoded.
const enc = new TextEncoder();
const dec = new TextDecoder();

export function toHex(buf) {
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
export function randomHex(bytes = 32) {
  const a = new Uint8Array(bytes);
  crypto.getRandomValues(a);
  return toHex(a);
}
// Uniform 6-digit code (rejection sampling avoids modulo bias)
export function randomOtp() {
  const a = new Uint32Array(1);
  const limit = Math.floor(0x100000000 / 1e6) * 1e6;
  do { crypto.getRandomValues(a); } while (a[0] >= limit);
  return String(a[0] % 1e6).padStart(6, "0");
}
export async function sha256Hex(s) {
  return toHex(await crypto.subtle.digest("SHA-256", enc.encode(s)));
}
export async function hmacHex(secret, msg) {
  if (!secret) throw new Error("missing HMAC secret");
  const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return toHex(await crypto.subtle.sign("HMAC", k, enc.encode(msg)));
}
// Constant-time compare that does not early-exit on length
export function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  const max = Math.max(a.length, b.length);
  let d = a.length ^ b.length;
  for (let i = 0; i < max; i++) d |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return d === 0;
}

function b64(u8) { let s = ""; for (const b of u8) s += String.fromCharCode(b); return btoa(s); }
function unb64(s) { return Uint8Array.from(atob(s), (c) => c.charCodeAt(0)); }

async function aesKey(env) {
  if (!env.PII_KEY) throw new Error("PII_KEY not configured");
  const raw = unb64(env.PII_KEY);
  if (raw.length !== 32) throw new Error("PII_KEY must be 32 bytes (base64)");
  return crypto.subtle.importKey("raw", raw, "AES-GCM", false, ["encrypt", "decrypt"]);
}
// AES-256-GCM, random 96-bit IV, record id bound as AAD (ciphertext cannot be moved between users)
export async function encryptPII(env, plain, aad = "") {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv, additionalData: enc.encode(aad) }, await aesKey(env), enc.encode(plain));
  return `v1.${b64(iv)}.${b64(new Uint8Array(ct))}`;
}
export async function decryptPII(env, token, aad = "") {
  const [v, iv, ct] = String(token).split(".");
  if (v !== "v1") throw new Error("unsupported ciphertext version");
  return dec.decode(await crypto.subtle.decrypt({ name: "AES-GCM", iv: unb64(iv), additionalData: enc.encode(aad) }, await aesKey(env), unb64(ct)));
}

// Strict validation instead of "strip dangerous characters"
export function normalizeIdentity(raw) {
  if (typeof raw !== "string" || raw.length > 320) return null;
  const v = raw.trim().toLowerCase();
  if (/^[a-z0-9._%+-]{1,64}@[a-z0-9.-]{1,190}\.[a-z]{2,24}$/.test(v)) return { kind: "email", value: v };
  const p = v.replace(/[\s-]/g, "");
  if (/^\+[1-9]\d{7,14}$/.test(p)) return { kind: "phone", value: p };
  return null;
}
export function maskIdentity({ kind, value }) {
  if (kind === "email") { const [u, d] = value.split("@"); return `${u[0]}***@${d}`; }
  return `${value.slice(0, 3)}${"*".repeat(Math.max(0, value.length - 5))}${value.slice(-2)}`;
}
