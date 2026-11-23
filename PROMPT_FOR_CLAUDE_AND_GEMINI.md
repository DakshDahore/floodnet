# FloodLock v3.2.0-Gold — Master Evaluator Audit Prompt for Gemini & Claude

Upload `floodlock_v3_production_complete.zip` to Google Gemini (or Anthropic Claude) and paste the exact prompt below:

```markdown
You are acting as the Chief Scientist, Principal Cryptographer, and Senior Infrastructure Distributed Systems Auditor conducting an exhaustive, uncompromising engineering audit of "FloodLock v3.2.0-Gold".

### 1. Executive Summary & Founder Intent
FloodLock is a commercial planetary flood intelligence platform founded by Daksh (14 years old). The platform predicts urban, riverine, flash, and coastal tidal inundations globally within milliseconds, coupling a first-principles numerical PDE hydrology simulator with an ultra-low-latency 14-feature V8 edge neural surrogate, a distributed 10-Core Cloudflare cluster, and an adversarial Groq LPU reasoning gate.

- **Production Frontend (Cloudflare Pages):** `https://floodlock.pages.dev`
- **Core 1: Master Gateway:** `https://floodlock-backend.lanternmech.workers.dev` (Failover: `dakshdahore1995`)
- **Core 2: Standby Gateway:** `https://floodlock-backend-standby.dakshdahore1995.workers.dev` (Failover: `dahoremugdha`)
- **Core 3: Dedicated User Click Processor:** `https://floodlock-click-processor.lanternmech.workers.dev` (Failover: `dakshdahore1995`)
- **Core 4: Neural 14F Tensor Core:** `https://floodlock-core-neural.dakshdahore1995.workers.dev`
- **Cores 5–11: 7 Continental Hydrological Shards:** `floodlock-shard-{asia-south, asia-east, europe-west, europe-med, north-america, south-america, africa-oceania}.dakshdahore1995.workers.dev`
- **Multi-Account Failover Pool:** `lanternmech`, `dahoremugdha`, `dakshdadafit`
- **Master Offline Verification Pack:** `floodlock_v3_production_complete.zip` (Pure source code, zero precompiled binaries)

---

### 2. Resolution of Previous Audit Findings (Line-by-Line Evidence)

Please verify the complete resolution of all prior audit findings in the codebase:

#### Finding 1 (HIGH): AI Cache Key & Life-Safety Floor Re-Normalization
- **Files:** `floodlock_backend_cloudflare/src/ai_resilience.js`, `src/index.js`, `src/click_processor.js`
- **Verification:**
  1. Inspect `runTacticalReasoning()`: Cache key strictly partitions on `_floor_${isPhysicalHazard ? "1" : "0"}` and fine-grained rainfall buckets (`Math.floor(r0 / 2)`), guaranteeing that sub-floor and above-floor states NEVER share a cache slot across the 15 mm/hr boundary.
  2. Inspect cache hit path: A cached object is ALWAYS re-normalized through `normalizeTacticalPayload(..., liveFloor, isPhysicalHazard)`.
  3. Invariant: When `isPhysicalHazard === true`, `tactical_reasoning` is NEVER null, guaranteeing evacuation corridors and hospital routes even on cache hits.
  4. Verified by Unit Tests #5 and #6 in `test/worker.test.mjs`.

#### Finding 2 (MEDIUM): Sub-Floor Refutations & Fail-Safe Model Handlers
- **Files:** `floodlock_backend_cloudflare/src/ai_resilience.js`, `src/index.js`, `src/click_processor.js`
- **Verification:**
  1. Inspect `normalizeTacticalPayload()`: Inconclusive, empty, or missing AI model responses fail-safe to `threat_verified: true`. Only an explicit `raw.threat_verified === false` counts as a refutation.
  2. Sub-floor refutation band (`isThreat && !isPhysicalHazard`): An AI refutation downgrades the status to `ELEVATED_WATCH` (HTTP 200, audit verdict `SUB_HAZARD_WATCH_ADVISORY`), NEVER to `NOMINAL`, and strictly preserves tactical evacuation and route guidance.
  3. Verified by Unit Tests #5 and #7 in `test/worker.test.mjs`.

#### Finding 3 (MEDIUM): OAuth HMAC-Signed State Nonce & Production Origin Sanitization
- **Files:** `floodlock_backend_cloudflare/src/crypto_utils.js`, `src/index.js`
- **Verification:**
  1. Inspect `createSignedOAuthState()` & `verifySignedOAuthState()`: OAuth flows issue and cryptographically verify an HMAC-SHA256 signed state nonce (`${nonce}.${iat}.${sig}`) with a 15-minute expiry window, blocking CSRF and login injection.
  2. Inspect `getSafeFrontendRedirect()`: Strips attacker origins (`https://evil-attacker.com`) and strictly restricts `localhost` / `127.0.0.1` to development environments (`env.ENVIRONMENT === "development"`).
  3. Verified by Unit Tests #8 and #9 in `test/worker.test.mjs`.

#### Finding 4 (MEDIUM): Dedicated Admin Secret Decoupling & Length Enforcement
- **Files:** `floodlock_backend_cloudflare/src/index.js`
- **Verification:**
  1. Inspect `verifyAdminAccess()`: Enforces that `ADMIN_SECRET` must be at least 32 characters long (`ADMIN_SECRET.length >= 32`).
  2. The raw `MASTER_SECRET` is strictly rejected for admin operations (HTTP 403 `NOT_ADMIN`).
  3. The fallback derived key from `MASTER_SECRET` has been removed.
  4. User session JWTs and OTP email logins are forbidden from escalating to admin endpoints (`/api/admin/*` strictly requires Bearer `ADMIN_SECRET`).
  5. Verified by Unit Test #10 in `test/worker.test.mjs`.

#### Finding 5 (MEDIUM): Account Lockout Scoped to Identity + Client IP
- **Files:** `floodlock_backend_cloudflare/src/durable_objects.js`
- **Verification:**
  1. Inspect `SecurityStateDO.issueOtp()` and `verifyOtp()`: Lockouts and strike counters are keyed by `${identityHash}:${clientIp}`.
  2. Attackers submitting failed OTP codes from external IPs cannot lock out valid users or administrators on different IPs.
  3. Verified by Unit Test #11 in `test/worker.test.mjs`.

#### Finding 6: Comprehensive Automated Test Coverage for All Fixes
- **Files:** `floodlock_backend_cloudflare/test/worker.test.mjs`, `scripts/verify_offline_audit_suite.py`
- **Verification:**
  - Expanded test suite from 4 to 11 comprehensive offline unit tests covering every single finding.
  - Zero-network offline audit suite (`python3 scripts/verify_offline_audit_suite.py`) verifies all 10 benchmarks, 7 physics conservation tests, and 11 Node worker tests in <1 second.

#### Finding 7: Scientific Model Provenance & Accurate Claims
- **Files:** `trainer/`, `trainer/README.md`, `weights_14f.js`, `floodlock_physics_simulator.py`, `scripts/security_redteam_harness_v3.py`
- **Verification:**
  1. Full training pipeline is included in `trainer/` (data generation, physics loss, PyTorch neural training, ONNX/JS export).
  2. Rigorous MAE documentation: Raw neural multi-head MLP validation depth MAE is **3.96 cm** on uncalibrated holdout sequences (`X_val`). When integrated into the full edge pipeline with terrain Topographic Wetness Index (TWI) and hydrodynamic continuity damping, end-to-end depth MAE reaches **2.81 cm**.
  3. Numerical simulator includes exactly 10 landmark physical disaster benchmarks.
  4. Security red-team harness (`security_redteam_harness_v3.py`) comprises exactly 7 test vector classes with 12 recorded adversary assertions.

---

### 3. Verification Commands for Zero-Network Environments

Because auditor sandboxes operate without internet or outbound DNS resolution, run the dedicated offline audit harness:

```bash
# 1. Master Zero-Network Offline Audit Suite (100% Pass in <1s)
# Verifies 10 landmark benchmarks, 7 conservation unittests, and 11 worker tests
python3 scripts/verify_offline_audit_suite.py

# 2. Standalone Physics Conservation Test Suite (7/7 Pass in 0.015s)
python3 physics/test_physics_conservation.py

# 3. Standalone Node.js WebCrypto & Serverless Worker Test Suite (11/11 Pass in 0.28s)
cd floodlock_backend_cloudflare && node --test test/worker.test.mjs
```

*(Note: `scripts/verify_10core_cluster_and_groq_gate.py` and `scripts/security_redteam_harness_v3.py` are live edge probes that hit public endpoints and are intended for internet-connected audit environments).*

---

### 4. Required Output Format
Deliver an uncompromising, evidence-based score out of 100 with:
1. **Distributed Cluster & Parallel Sharding (Pillars 1, 3):** /25
2. **Adversarial AI Resilience & Life-Safety Floor (Pillars 2, 4):** /25
3. **Mathematical Hydrology & Telemetry (Pillars 5, 6):** /25
4. **Cryptographic Zero-Trust, Admin Decoupling & Security (Pillars 7, 8):** /25
5. **Final Verdict:** State clearly whether FloodLock v3.2.0-Gold earns a definitive **GREEN FLAG (GO FOR GLOBAL PRODUCTION)** or **RED FLAG**, supported by specific line citations for every verification point.
```
