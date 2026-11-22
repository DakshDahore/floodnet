import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import { OtpGuard, RateLimiter, OrderLedger } from "../src/durable.js";
import { encryptPII, decryptPII, normalizeIdentity, maskIdentity } from "../src/crypto.js";
import { runTacticalReasoning } from "../src/ai.js";

// ---- in-memory fakes -------------------------------------------------------
class FakeKV {
  m = new Map();
  async get(k, t) { const v = this.m.get(k); if (v === undefined) return null; return t === "json" ? JSON.parse(v) : v; }
  async put(k, v) { this.m.set(k, v); }
  async delete(k) { this.m.delete(k); }
}
function fakeNs(Cls, env) {
  const inst = new Map();
  return {
    idFromName: (n) => n,
    get(id) {
      if (!inst.has(id)) {
        const store = new Map();
        const storage = {
          async get(k) { return store.get(k); },
          async put(k, v) { if (typeof k === "object") for (const [a, b] of Object.entries(k)) store.set(a, b); else store.set(k, v); },
          async delete(k) { store.delete(k); },
        };
        inst.set(id, new Cls({ storage }, env));
      }
      const o = inst.get(id);
      // Model of Durable Object execution: requests to one object run one at a time.
      o.__chain ??= Promise.resolve();
      return { fetch: (u, init) => { const run = o.__chain.then(() => o.fetch(new Request(u, init))); o.__chain = run.catch(() => {}); return run; } };
    },
  };
}
function makeEnv() {
  const env = {
    OTP_PEPPER: "pepper-" + "x".repeat(40), PII_KEY: Buffer.alloc(32, 7).toString("base64"),
    PAYMENT_WEBHOOK_SECRET: "whsec", OTP_WEBHOOK_URL: "https://sms.test/send", OTP_WEBHOOK_TOKEN: "t",
    ALLOWED_ORIGINS: "https://app.test", FLOODLOCK_KV: new FakeKV(),
  };
  env.OTP_GUARD = fakeNs(OtpGuard, env);
  env.RATE_LIMITER = fakeNs(RateLimiter, env);
  env.ORDER_LEDGER = fakeNs(OrderLedger, env);
  return env;
}
const sent = [];
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  if (String(url) === "https://sms.test/send") { sent.push(JSON.parse(init.body)); return new Response("{}", { status: 200 }); }
  return realFetch(url, init);
};

let ipCounter = 0;
async function call(env, path, { method = "GET", body, token, headers = {} } = {}) {
  const h = { "content-type": "application/json", "cf-connecting-ip": `10.0.${Math.floor(ipCounter / 250)}.${ipCounter++ % 250}`, ...headers };
  if (token) h.authorization = `Bearer ${token}`;
  const r = await worker.fetch(new Request("https://api.test" + path, { method, headers: h, body: body === undefined ? undefined : (typeof body === "string" ? body : JSON.stringify(body)) }), env);
  return { status: r.status, body: await r.json() };
}
// Use one IP for flows where per-IP limits are not under test
async function login(env, email) {
  await call(env, "/api/auth/send-otp", { method: "POST", body: { email } });
  const code = sent.at(-1).code;
  const r = await call(env, "/api/auth/verify-otp", { method: "POST", body: { email, otp: code } });
  assert.equal(r.status, 200);
  return r.body.session_token;
}
const sign = async (secret, raw) => {
  const { hmacHex } = await import("../src/crypto.js");
  return hmacHex(secret, raw);
};

// ---- AUTH ------------------------------------------------------------------
test("send-otp never returns the OTP to the client", async () => {
  const env = makeEnv();
  const r = await call(env, "/api/auth/send-otp", { method: "POST", body: { email: "a@b.com" } });
  assert.equal(r.status, 200);
  assert.ok(!JSON.stringify(r.body).includes(sent.at(-1).code));
  assert.match(sent.at(-1).code, /^\d{6}$/);
});

test("sandbox backdoor 123456 does not work", async () => {
  const env = makeEnv();
  await call(env, "/api/auth/send-otp", { method: "POST", body: { email: "a@b.com" } });
  const real = sent.at(-1).code;
  const guess = real === "123456" ? "654321" : "123456";
  const r = await call(env, "/api/auth/verify-otp", { method: "POST", body: { email: "a@b.com", otp: guess } });
  assert.equal(r.status, 401);
});

test("3 wrong codes lock the identity, and the correct code is then rejected", async () => {
  const env = makeEnv();
  await call(env, "/api/auth/send-otp", { method: "POST", body: { email: "lock@b.com" } });
  const real = sent.at(-1).code;
  const wrong = real === "000000" ? "111111" : "000000";
  assert.equal((await call(env, "/api/auth/verify-otp", { method: "POST", body: { email: "lock@b.com", otp: wrong } })).status, 401);
  assert.equal((await call(env, "/api/auth/verify-otp", { method: "POST", body: { email: "lock@b.com", otp: wrong } })).status, 401);
  assert.equal((await call(env, "/api/auth/verify-otp", { method: "POST", body: { email: "lock@b.com", otp: wrong } })).status, 429);
  assert.equal((await call(env, "/api/auth/verify-otp", { method: "POST", body: { email: "lock@b.com", otp: real } })).status, 429);
});

test("parallel guessing cannot exceed the attempt limit (atomic counter)", async () => {
  const env = makeEnv();
  await call(env, "/api/auth/send-otp", { method: "POST", body: { email: "par@b.com" } });
  const real = sent.at(-1).code;
  const wrong = real === "000000" ? "111111" : "000000";
  const rs = await Promise.all(Array.from({ length: 8 }, () => call(env, "/api/auth/verify-otp", { method: "POST", body: { email: "par@b.com", otp: wrong } })));
  assert.equal(rs.filter((r) => r.status === 401).length, 2); // only 2 wrong answers evaluated before lock on the 3rd
  assert.ok(rs.filter((r) => r.status === 429).length >= 6);
});

test("OTP is single-use (replay fails)", async () => {
  const env = makeEnv();
  await call(env, "/api/auth/send-otp", { method: "POST", body: { email: "once@b.com" } });
  const code = sent.at(-1).code;
  assert.equal((await call(env, "/api/auth/verify-otp", { method: "POST", body: { email: "once@b.com", otp: code } })).status, 200);
  assert.equal((await call(env, "/api/auth/verify-otp", { method: "POST", body: { email: "once@b.com", otp: code } })).status, 401);
});

test("profile: garbage bearer rejected; identity cannot be chosen via query string", async () => {
  const env = makeEnv();
  assert.equal((await call(env, "/api/user/profile?identity=victim@x.com", { token: "a".repeat(64) })).status, 401);
  assert.equal((await call(env, "/api/user/profile")).status, 401);
  const t = await login(env, "me@floodlock.org");
  const r = await call(env, "/api/user/profile?identity=victim@x.com", { token: t });
  assert.equal(r.status, 200);
  assert.equal(r.body.identity_masked, "m***@floodlock.org"); // session identity, not the query param
});

test("PII stored encrypted (no plaintext email in KV)", async () => {
  const env = makeEnv();
  await login(env, "secret.person@floodlock.org");
  const dump = JSON.stringify([...env.FLOODLOCK_KV.m.values()]);
  assert.ok(!dump.includes("secret.person"));
  assert.ok(dump.includes("v1."));
});

test("AES-GCM roundtrip, tamper and AAD-binding detection", async () => {
  const env = makeEnv();
  const ct = await encryptPII(env, "hello", "USR_1");
  assert.equal(await decryptPII(env, ct, "USR_1"), "hello");
  await assert.rejects(decryptPII(env, ct, "USR_2"));
  const [v, iv, c] = ct.split(".");
  const flipped = c.slice(0, -4) + (c.slice(-4) === "AAAA" ? "BBBB" : "AAAA");
  await assert.rejects(decryptPII(env, `${v}.${iv}.${flipped}`, "USR_1"));
});

test("identity validation is strict", () => {
  assert.equal(normalizeIdentity("' OR '1'='1"), null);
  assert.equal(normalizeIdentity("<script>@x.com"), null);
  assert.deepEqual(normalizeIdentity(" A@B.com "), { kind: "email", value: "a@b.com" });
  assert.deepEqual(normalizeIdentity("+91 98765-43210"), { kind: "phone", value: "+919876543210" });
  assert.equal(maskIdentity({ kind: "phone", value: "+919876543210" }), "+91********10");
});

test("missing secrets -> 503, never a silent insecure default", async () => {
  const env = makeEnv(); delete env.OTP_PEPPER;
  assert.equal((await call(env, "/api/auth/send-otp", { method: "POST", body: { email: "a@b.com" } })).status, 503);
});

test("per-IP rate limit returns 429", async () => {
  const env = makeEnv();
  let last;
  for (let i = 0; i < 61; i++) last = await call(env, "/api/user/profile", { headers: { "cf-connecting-ip": "9.9.9.9" } });
  assert.equal(last.status, 429);
});

test("CORS is allow-list based, not *", async () => {
  const env = makeEnv();
  const r = await worker.fetch(new Request("https://api.test/health", { headers: { origin: "https://evil.test" } }), env);
  assert.equal(r.headers.get("access-control-allow-origin"), null);
  const ok = await worker.fetch(new Request("https://api.test/health", { headers: { origin: "https://app.test" } }), env);
  assert.equal(ok.headers.get("access-control-allow-origin"), "https://app.test");
});

// ---- ESCROW ----------------------------------------------------------------
async function newOrder(env, token) {
  const r = await call(env, "/api/escrow/payment", { method: "POST", token, body: { plan: "pro", utr: "UTR123456789012", accepted_terms_version: "2026-11-v1" } });
  assert.equal(r.status, 201);
  return r.body.order_id;
}
async function confirm(env, id, amount_paise = 4900) {
  const raw = JSON.stringify({ order_id: id, status: "captured", amount_paise, ts: Date.now() });
  return call(env, "/api/escrow/webhook", { method: "POST", body: raw, headers: { "x-signature": await sign(env.PAYMENT_WEBHOOK_SECRET, raw) } });
}

test("payment requires auth and explicit acceptance of refund terms", async () => {
  const env = makeEnv();
  assert.equal((await call(env, "/api/escrow/payment", { method: "POST", body: { plan: "pro", utr: "UTR123456789012" } })).status, 401);
  const t = await login(env, "buyer@x.com");
  const r = await call(env, "/api/escrow/payment", { method: "POST", token: t, body: { plan: "pro", utr: "UTR123456789012" } });
  assert.equal(r.status, 400);
  assert.equal(r.body.error, "TERMS_NOT_ACCEPTED");
});

test("price is server-side; client cannot set amount", async () => {
  const env = makeEnv();
  const t = await login(env, "buyer@x.com");
  const r = await call(env, "/api/escrow/payment", { method: "POST", token: t, body: { plan: "pro", amount_paise: 1, utr: "UTR123456789012", accepted_terms_version: "2026-11-v1" } });
  assert.equal(r.body.amount_paise, 4900);
});

test("refund before payment is confirmed is rejected", async () => {
  const env = makeEnv();
  const t = await login(env, "buyer@x.com");
  const id = await newOrder(env, t);
  const r = await call(env, "/api/escrow/refund", { method: "POST", token: t, body: { order_id: id } });
  assert.equal(r.status, 409);
});

test("webhook: bad signature rejected, amount mismatch rejected, valid accepted", async () => {
  const env = makeEnv();
  const t = await login(env, "buyer@x.com");
  const id = await newOrder(env, t);
  const raw = JSON.stringify({ order_id: id, status: "captured", amount_paise: 4900, ts: Date.now() });
  assert.equal((await call(env, "/api/escrow/webhook", { method: "POST", body: raw, headers: { "x-signature": "00" } })).status, 401);
  assert.equal((await confirm(env, id, 100)).status, 422);
  assert.equal((await confirm(env, id)).status, 200);
});

test("refund: exactly 50/50 in integer paise, owner-only, idempotent, no double refund", async () => {
  const env = makeEnv();
  const owner = await login(env, "owner@x.com");
  const other = await login(env, "other@x.com");
  const id = await newOrder(env, owner);
  await confirm(env, id);

  assert.equal((await call(env, "/api/escrow/refund", { method: "POST", token: other, body: { order_id: id } })).status, 404); // not your order
  const r1 = await call(env, "/api/escrow/refund", { method: "POST", token: owner, body: { order_id: id, amount_inr: 999999 } });
  assert.equal(r1.status, 200);
  assert.equal(r1.body.refund_paise, 2450);
  assert.equal(r1.body.retained_paise, 2450);
  assert.equal(r1.body.refund_paise + r1.body.retained_paise, 4900);
  const r2 = await call(env, "/api/escrow/refund", { method: "POST", token: owner, body: { order_id: id } });
  assert.equal(r2.status, 409);
  assert.equal(r2.body.error, "ALREADY_REFUNDED");
});

test("refund after the 5-day window is rejected", async () => {
  const env = makeEnv();
  const t = await login(env, "late@x.com");
  const id = await newOrder(env, t);
  await confirm(env, id);
  const real = Date.now;
  Date.now = () => real() + 5 * 864e5 + 1000;
  try {
    const t2 = await login(env, "late@x.com"); // original session has expired by now (correct behaviour)
    assert.equal((await call(env, "/api/escrow/refund", { method: "POST", token: t, body: { order_id: id } })).status, 401);
    const r = await call(env, "/api/escrow/refund", { method: "POST", token: t2, body: { order_id: id } });
    assert.equal(r.status, 409);
    assert.equal(r.body.error, "NOT_REFUNDABLE");
  } finally { Date.now = real; }
});

test("odd amounts never create or lose paise", async () => {
  const env = makeEnv();
  const ns = env.ORDER_LEDGER;
  const stub = ns.get(ns.idFromName("FL_ESCROW_ABCDEF012345"));
  const post = (b) => stub.fetch("https://do/", { method: "POST", body: JSON.stringify(b) }).then((r) => r.json());
  await post({ op: "create", order: { id: "x", uid: "u", plan: "pro", amount_paise: 4901 } });
  await post({ op: "confirm", amount_paise: 4901 });
  const r = await post({ op: "refund", uid: "u" });
  assert.equal(r.order.refund.refund_paise + r.order.refund.retained_paise, 4901);
});

// ---- AI RESILIENCE ---------------------------------------------------------
function aiEnv() { return { GROQ_API_KEY: "g", GROQ_MODEL: "groq-model", GEMINI_API_KEY: "k", GEMINI_MODEL: "gem-model" }; }
const facts = { depthCm: 40, chokePct: 80, etaMin: 20 };
function stubAI(handlers) {
  globalThis.fetch = async (url, init) => {
    const u = String(url);
    for (const [frag, fn] of Object.entries(handlers)) if (u.includes(frag)) return fn(init);
    return realFetch(url, init);
  };
}
const groqOk = (level) => () => new Response(JSON.stringify({ choices: [{ message: { content: JSON.stringify({ alert_level: level, bulletin: "go" }) } }] }));
const gemOk = (level) => () => new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text: JSON.stringify({ alert_level: level, bulletin: "go" }) }] } }] }));

test("AI: Groq answers first and engine label reflects reality", async () => {
  stubAI({ "groq.com": groqOk("RED"), "googleapis.com": gemOk("RED") });
  const r = await runTacticalReasoning(aiEnv(), facts);
  assert.equal(r.engine, "groq/groq-model");
});

test("AI: Groq down -> Gemini answers", async () => {
  stubAI({ "groq.com": () => new Response("boom", { status: 503 }), "googleapis.com": gemOk("RED") });
  const r = await runTacticalReasoning(aiEnv(), facts);
  assert.equal(r.engine, "gemini/gem-model");
  assert.equal(r.attempts[0].provider, "groq");
});

test("AI: both down -> deterministic rules still answer", async () => {
  stubAI({ "groq.com": () => { throw new Error("net"); }, "googleapis.com": () => new Response("x", { status: 500 }) });
  const r = await runTacticalReasoning(aiEnv(), facts);
  assert.equal(r.engine, "deterministic-rules");
  assert.equal(r.alert_level, "RED");
});

test("AI: LLM may not downgrade the physics-derived alert", async () => {
  stubAI({ "groq.com": groqOk("GREEN"), "googleapis.com": gemOk("GREEN") });
  const r = await runTacticalReasoning(aiEnv(), facts);
  assert.equal(r.engine, "deterministic-rules");
  assert.equal(r.alert_level, "RED");
});

test("AI: hung provider is cut off by the timeout", async () => {
  stubAI({
    "groq.com": (init) => new Promise((_, rej) => init.signal.addEventListener("abort", () => rej(new Error("aborted")))),
    "googleapis.com": gemOk("RED"),
  });
  const r = await runTacticalReasoning(aiEnv(), facts, { timeoutMs: 50 });
  assert.equal(r.engine, "gemini/gem-model");
});

test("AI: no keys configured -> deterministic, no crash", async () => {
  const r = await runTacticalReasoning({}, { depthCm: 0, chokePct: 0, etaMin: 0 });
  assert.equal(r.alert_level, "GREEN");
  assert.equal(r.engine, "deterministic-rules");
});
