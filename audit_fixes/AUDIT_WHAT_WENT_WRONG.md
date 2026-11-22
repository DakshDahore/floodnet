# FloodLock: Where It Went Wrong, and What Was Fixed

**Scope:** source-code audit of `floodlock_complete_v2_verification_pack.zip` and `FLOODLOCK_MASTER_VERIFICATION_SPEC.md`. I could not inspect the deployed Worker, so everything below is about the code as shipped in the pack.
**Not legal advice.** The escrow section flags risks for a lawyer to review.

---

## 1. The short version

The spec describes a system that is secure, physically conserved and legally robust. The code does not back that up. Three root causes explain almost everything:

1. **Claims were written before the code and tests existed.** "100% repelled", "AES-256", "zero-breach", "calibrated to 10 disasters" are assertions in strings and comments, not behaviours anyone verified.
2. **Test-friendly shortcuts shipped to production.** A `123456` OTP backdoor, a hardcoded API key and a hardcoded signing secret were all convenient in development and never removed.
3. **The wrong storage primitive for the job.** Attempt counters, single-use codes and order states were put in Cloudflare KV, which is eventually consistent. Security counters and money state need strong consistency.

| # | Area | Severity | Problem (short) | Fixed in |
|---|---|---|---|---|
| 1 | Security | **Critical** | Live Groq API key hardcoded in source | `src/ai.js`, `wrangler.jsonc` |
| 2 | Security | **Critical** | `MASTER_SECRET` hardcoded; signs OTPs, challenge tokens, sessions | `src/crypto.js`, `src/durable.js` |
| 3 | Security | **Critical** | `123456` accepted as a valid OTP for any identity | `src/durable.js` |
| 4 | Security | **Critical** | Bearer token never verified; identity taken from query string | `src/index.js` |
| 5 | Money | **Critical** | Refund endpoint: no auth, client sets amount, no window check | `src/durable.js` `OrderLedger` |
| 6 | Security | High | Lockout bypassable (no KV = no limit; KV races) | `OtpGuard` Durable Object |
| 7 | Security | High | "AES-256 encryption" does not exist; only `substring + "***"` | `src/crypto.js` |
| 8 | Security | High | Rate limiter claimed but absent; CORS `*`; client-supplied LLM keys | `src/index.js` |
| 9 | Security | Medium | Blocklist "sanitiser" mutates input and is bypassable | `normalizeIdentity` |
| 10 | Physics | **High** | Water created from nothing (1.5 cm at zero rain) | `floodlock_physics_fixed.py` |
| 11 | Physics | High | Magic constants break units; Manning "Q" is not a discharge | same |
| 12 | Physics | High | "+1h/+3h/+6h" targets are really +10/+30/+60 min | same |
| 13 | Physics | Medium | Green-Ampt hacks; depression storage was cosmetic | same |
| 14 | Physics | Medium | "Calibrated to 10 disasters" and "MAE 2.81 cm" overstated | doc only (needs real data) |
| 15 | AI | Medium | Deployed backend uses a different model chain than the spec | `src/ai.js` |
| 16 | AI | Medium | Engine label hardcoded, so provenance can be wrong | `src/ai.js` |
| 17 | AI | Medium | LLM output could contradict the physics-derived alert | `src/ai.js` |
| 18 | Escrow | High | Not a real escrow; policy and enforcement gaps | `src/index.js`, `src/durable.js` |
| 19 | Spec | Medium | Spec points at files and a deployment that don't match the pack | this doc |

---

## 2. Security findings

### 1. Hardcoded Groq API key (Critical)
**What the code did:** `const groqKey = env.GROQ_API_KEY || "gsk_dd…"`. A real-looking key was the fallback in `backend/index.js`.
**Why it's wrong:** anyone with the repo, a zip, a screenshot or a leaked git history owns your Groq quota. It was also included in the pack you uploaded for audit.
**Do this first:** rotate the key in the Groq console (assume it's compromised), then scrub git history (`git filter-repo` or BFG). Rotating alone is not enough if the key stays in history.
**Fix:** keys come only from `env` (`wrangler secret put GROQ_API_KEY`). If the secret is missing, that provider is skipped.

### 2. Hardcoded `MASTER_SECRET` (Critical)
**What the code did:** one constant string in source signed OTP hashes, the stateless challenge tokens and session tokens.
**Why it's wrong:** anyone who has read the repo can forge a valid challenge token or session token for any user. One secret in three roles also means one leak breaks everything.
**Fix:** `OTP_PEPPER` is a Wrangler secret used only for OTP/identity hashing. Session tokens are now **random** (256 bits), so there is nothing to forge. Only a hash of the token is stored server-side.

### 3. `123456` sandbox OTP (Critical)
**What the code did:** `const isSandboxCode = submittedOtp === "123456"`, and when true, `isValid = true` for **any** identity.
**Why it's wrong:** it's an authentication bypass, since anyone can log in as anyone. It also skipped the attempt counter, so the 3-strike lockout never applied to it.
**Fix:** removed. Test: `sandbox backdoor 123456 does not work`.

### 4. Tokens were never verified (Critical)
**What the code did:** `/api/user/profile` only checked `authHeader.startsWith("Bearer ")` and then loaded the profile for `?identity=` from the query string.
**Why it's wrong:** `Authorization: Bearer lol` plus `?identity=victim@x.com` returned the victim's profile. The session token was `HMAC(user_id:timestamp)` and nothing stored or checked it, so it couldn't be validated or revoked.
**Fix:** opaque random token, looked up in KV by its SHA-256, expiry enforced, and the identity comes from the **session**, not the request. Test: `profile: garbage bearer rejected; identity cannot be chosen via query string`.

### 5. Unauthenticated refund endpoint (Critical, money)
**What the code did:** `amountInr = parseFloat(body.amount_inr || 49.0)`, then 50% was "refunded". There was no login, no order lookup, no owner check, no 5-day check, no idempotency.
**Why it's wrong:** an attacker can mark any order refunded, repeatedly, with any amount. The `containsMaliciousPayload` check on the order ID doesn't help, because the flaw is authorisation, not injection.
**Fix:** `OrderLedger` Durable Object is the only thing that changes order state. Refund requires a session, the order's owner, status `HELD`, inside the window, and not already refunded. Amounts are computed server-side in **integer paise** (`floor(amount/2)`, remainder retained, so no paise are created or lost). Tests cover owner-only, idempotency, window expiry, and `amount_inr: 999999` being ignored.

### 6. The lockout didn't really lock (High)
**What the code did:** the 3-strike counter lived in KV, and only when `env.FLOODLOCK_KV` was bound. Otherwise it fell back to a stateless token with **no attempt limit at all**.
**Why it's wrong:** (a) with no KV there's unlimited guessing of a 6-digit code (1,000,000 possibilities); (b) with KV, read-increment-write is racy and KV is eventually consistent, so parallel guesses from several edge locations can far exceed 3.
**Fix:** `OtpGuard` Durable Object, one per identity. It holds the OTP hash, fail counter and lock, with strongly consistent single-threaded storage. The OTP is **single-use** and consumed atomically. A missing/expired OTP still counts as a failure, so attackers can't probe for free. Test: `parallel guessing cannot exceed the attempt limit`.
**Known trade-off:** per-identity lockout lets an attacker lock a victim out for 15 minutes by guessing wrong. Per-IP rate limits mitigate it. For higher assurance, add CAPTCHA/Turnstile and prefer magic links or passkeys.

### 7. "AES-256" was a label (High)
**What the code did:** no `encrypt` call anywhere. "Masking" was `identity.substring(0,3) + "***"`, and the response said `"AES-256 PII Encrypted at Rest (GDPR & Indian DPDP Compliant)"`.
**Why it's wrong:** masking is a display choice, not encryption. The compliance claim was false, and false compliance claims are a liability.
**Fix:** real **AES-256-GCM** with a random 96-bit IV and the user id bound as AAD (a ciphertext can't be moved to another user). Key from `PII_KEY` secret. Display masking is separate. Tests: roundtrip, tamper detection, AAD binding, and "no plaintext email in KV".
**Not covered:** key rotation, KMS, and an actual DPDP/GDPR compliance programme. Remove the compliance wording until you have one.

### 8. Missing rate limiting, open CORS, client-supplied LLM keys (High)
The spec promised 60 req/min per IP, but no limiter existed. `CORS: *` plus an `x-gemini-api-key` header let any website use your endpoint as a free LLM proxy.
**Fix:** per-IP limits via a `RateLimiter` Durable Object (stricter on OTP routes), an allow-list CORS policy, and no client-supplied provider keys.

### 9. The "sanitiser" approach (Medium)
Stripping characters like `' " ; ( ) < >` and regex-blocklisting `union select` is bypassable and also **changes valid input**. Injection is prevented by parameterised access (KV keys aren't SQL anyway) and strict validation.
**Fix:** `normalizeIdentity` accepts only well-formed email or E.164 phone and rejects everything else. Order IDs must match `^FL_ESCROW_[0-9A-F]{12}$`.

### About the "100% repelled / 80 vectors" red-team claim
- The harness's own docstring says "100+ to 1,000" vectors; the spec says 80.
- It never tested the vulnerabilities above (backdoor OTP, token forgery, unauthenticated refund). It tested payload strings like `<script>` against a service whose real flaws were logic flaws.
- V8 isolates remove OS/SSH-level attack surface, which is genuinely good. They do nothing for authorisation bugs.
- "100% success rate" on a test suite means the suite is narrow, not that the system is unbreakable.

---

## 3. Physics findings (Engine 1)

### 10. Water created from nothing (High)
Original behaviour: when `tide > invert`, `backwater_inflow_m = choke_ratio * 0.02 * dt/3600` was added **unconditionally**.
I ran it: **zero rain, 4.48 m tide, permeable catchment → 1.5 cm depth.** That directly violates the spec's own rule ("depth can never exceed net rain plus backwater") and the "Sahara must be exactly 0.0 cm" gate for any coastal location. The training data hid it because the dry archetype used `tide ≤ 0.8 m`, below the pipe invert.
**Fix:** push-back only occurs if the surface is already ponded (surcharged), and it draws from a **finite tidal reservoir** that depletes. An explicit mass ledger tracks every term and the run **raises `MassBalanceError`** if the residual exceeds 1e-9 m.
**Modelling assumption to review:** real seawater overtopping at a dry shoreline is a separate surge process and is not modelled here. If you need it, make it an explicit boundary input, not a hidden source term.

### 11. Units and magic numbers (High)
Original: Manning `q` per metre width (m²/s) was divided by a bare `100` to become a depth change, and reported `runoff_q_m3s = q * 10`. Neither number came from catchment geometry, so the output wasn't a discharge.
**Fix:** depth change = `q·dt / flow_length_m`; discharge = `q × outlet_width_m`. Both lengths are explicit parameters you must set from real catchment data.

### 12. Mislabelled horizons (High)
Original: 6 steps × 600 s = 1 hour of total simulation, but targets were labelled "+1h, +3h, +6h" using indices `[0]`, `[2]`, `[-1]` (the first, `min(0, …)`, is always 0). They were actually **+10 min, +30 min, +60 min**.
**Fix:** 36 ten-minute reports over 6 h; targets are at the real +1h, +3h and +6h. **Any model trained on the old CSVs learned the wrong horizons and must be retrained.**

### 13. Green-Ampt and depression storage (Medium)
The first step used a `Ks × 8` hack, infiltration only applied to incoming rain (not water already ponded), and the 0.5 cm depression storage was subtracted only from the printed number, so water below it still flowed.
**Fix:** floored `F`, capacity limited to water actually available, ponded water infiltrates on the pervious fraction, and depression storage is real state (below it, nothing flows). The sub-step is 60 s and outflow is clamped so depth can't go negative.

### 14. Overstated validation (Medium, no code fix possible)
- **"Calibrated against 10 disasters":** the generator samples parameter ranges inspired by those events. There is no comparison to observed depths, gauges or inundation maps. Say "scenario-inspired", not "calibrated".
- **"MAE 2.81 cm proves physical generalisation":** the 85/15 split is correct practice against memorisation, but train and validation both come from the same simulator. It measures how well the neural net copies the simulator, not how well either matches reality.
- **"30-metre resolution":** this is a lumped single-cell model. Per-pixel 30 m output isn't produced by what's in the pack.
- This is not the 2D Saint-Venant system the spec text describes; it is a kinematic-style lumped approximation. Real calibration needs observed data (e.g. event hydrographs and flood-extent maps).

**Verification of the fix:** `physics/test_physics_conservation.py` has 9 tests: zero-rain high-tide is exactly 0.0; Sahara control; 1,500 random basins with residual < 1e-9, no negatives, and depth ≤ everything that entered; correct horizon indices; higher tide never lowers depth; backwater bounded by the reservoir; invalid inputs rejected; and a deliberate mass-injection that the guard must catch. All pass.

---

## 4. AI resilience findings

### 15. Spec ≠ deployed code
The spec says Qwen-3.8-27B on Groq → Gemini 1.5 Flash. The Worker in `backend_cloudflare/` (the one with the `AI` binding) uses **Workers AI Qwen 2.5 0.5B → Gemini 2.5 Flash → rules**. The Groq → Gemini code lives in a different, older file. Decide which backend is the real one and delete the other.
I also can't confirm a model called "Qwen-3.8-27B" exists on Groq. Check Groq's current model list, and check that the Gemini model ID you use is a currently supported GA model (1.5 Flash has been retired by Google).

### 16. Hardcoded engine labels
The code returned `engine: "Qwen-3.8-27B-Groq"` as a string regardless of which model answered, so your audit trail could be wrong.
**Fix:** model IDs come from `GROQ_MODEL`/`GEMINI_MODEL`; the reported engine is `provider/model` of the one that actually answered, or `deterministic-rules`.

### 17. LLM could contradict the physics
**Fix:** the alert level is computed deterministically first. The LLM can only add wording; if it returns a lower level, the answer is rejected and the next provider (then the rules) is used. Also added: hard timeouts (a hung provider can't stall the chain), the Gemini key in a header (not in the URL, which gets logged), and numeric-only inputs to the prompt (no injection through free text).
**Placeholder warning:** the alert thresholds (30 cm / 15 cm / 5 cm, choke %) are placeholders. They must come from the responsible flood authority, because this is life-safety messaging.

Tests: Groq answers first; Groq down → Gemini; both down → rules; downgrade rejected; timeout works; no keys → still answers.

---

## 5. Escrow findings

### 18. Not an escrow, and enforcement was missing
- **What it actually was:** a database record, an email alert and manual UTR references. No licensed escrow agent, nodal/payment-aggregator account or gateway holds the money, so calling it "escrow" and "T+5 settlement lock" is inaccurate. Holding customer funds this way may also raise RBI payment-system rules. Ask a lawyer or your payment provider before launch.
- **Refund policy:** keeping 50% of a ₹49 purchase and describing it as "GPU compute costs" is hard to justify as a real cost estimate and may be challenged as an unfair term. The retention must be disclosed **before** purchase, accepted explicitly, and reviewed against the Consumer Protection (E-Commerce) Rules, 2020, plus GST treatment of the retained amount.
- **Enforcement:** see finding 5.

**What I changed:**
- Payment requires login and **explicit acceptance of a versioned refund-terms string** (`TERMS_NOT_ACCEPTED` otherwise). The version is stored on the order.
- Price is server-side from a plan table. The client cannot set it.
- An order starts as `PENDING_PAYMENT` and becomes `HELD` only through a **signed, timestamped payment-gateway webhook**, so a user-typed UTR can't create "held" money. Amount mismatch is rejected.
- T+5 runs from confirmed payment. After that, refund is rejected as not refundable.
- Refund result is `REFUND_PENDING_PAYOUT`. **No money moves in this code.** A real payout needs your gateway's refund API (stubbed via an optional `REFUND_QUEUE`).
- The personal founder Gmail is no longer in API responses.

---

## 6. What the fixes do NOT cover (be honest with yourself)

- **Nothing here has been deployed or tested on real Cloudflare.** Tests run in Node with in-memory fakes. Durable Objects are modelled as one-request-at-a-time per object; I also structured the OTP check so the read-modify-write section has no non-storage `await`, which is what real Durable Objects need. Re-test on a real deployment (`wrangler dev`) before trusting it.
- **No real OTP delivery.** `sendOtp` calls a webhook you configure (SMS/email provider). The original returned `mock_delivery: "SUCCESS"`; that's gone, and delivery failure now returns 502.
- **Session revocation lag:** sessions live in KV, which can take up to ~60 s to propagate a deletion. Fine for this use; use a Durable Object if you need instant revocation.
- **Payment gateway, refunds, invoices, GST, KYC:** not implemented.
- **Physics calibration and the neural surrogate:** the new simulator changes the training targets, so the surrogate and the weights in `weights.js` must be regenerated and re-validated against **real** observations.
- **Legal/compliance:** DPDP/GDPR, RBI, consumer-law and terms-of-service work needs a qualified professional.
- **Frontend and the other backend** (`backend/app.py`, Render config, the hardcoded-URL scripts) were not audited in depth.

---

## 7. Do this in order

1. **Today:** rotate the Groq key (and Gemini, if one was ever committed), purge it from git history, and remove the `123456` backdoor.
2. Delete the duplicate backend; keep one source of truth.
3. Deploy the fixed Worker: `wrangler kv namespace create FLOODLOCK_KV`, set all secrets (see `wrangler.jsonc` comments), then `wrangler dev` and rerun the tests' scenarios against it.
4. Hook up a real OTP provider and a real payment gateway; don't launch paid plans before that.
5. Regenerate datasets with `floodlock_physics_fixed.py`, retrain, and validate against real flood data.
6. Remove or rewrite these claims until they are true: "AES-256 encrypted at rest", "zero-breach", "100% repelled", "GDPR/DPDP compliant", "escrow", "calibrated to 10 disasters", "30 m resolution".
7. Get independent review: a penetration test and a lawyer for the escrow terms.

---

## 8. Files and how to run

```
floodlock_fixes/
├── AUDIT_WHAT_WENT_WRONG.md           ← this file
├── physics/
│   ├── floodlock_physics_fixed.py     ← corrected Engine 1 with mass ledger
│   └── test_physics_conservation.py   ← python test_physics_conservation.py   (9 tests)
└── backend/
    ├── package.json  wrangler.jsonc  .dev.vars.example  .gitignore
    ├── src/crypto.js    ← HMAC, AES-256-GCM, OTP, strict identity validation
    ├── src/durable.js   ← OtpGuard, RateLimiter, OrderLedger (Durable Objects)
    ├── src/ai.js        ← Groq → Gemini → deterministic rules
    ├── src/index.js     ← router: sessions, rate limits, escrow, CORS allow-list
    └── test/backend.test.mjs   ← node --test test/backend.test.mjs   (25 tests)
```

Last verified run: physics **9/9** passing, backend **25/25** passing (Node 22).
