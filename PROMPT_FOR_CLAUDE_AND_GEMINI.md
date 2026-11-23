# FloodLock v3.2.0 — Auditor Evaluation Prompt for Claude & Gemini

Upload the offline verification archive to Anthropic Claude or Google Gemini and paste the prompt below:

```markdown
You are acting as an independent, adversarial Senior Security & Systems Auditor conducting a thorough, unbiased evaluation of FloodLock v3.2.0. Please examine the codebase, execute all offline test harnesses, and find anything wrong, insecure, fragile, or scientifically inaccurate across the implementation.

### 1. System Overview & Architecture
FloodLock is an urban and coastal flood intelligence system designed to predict inundation risks by coupling a zero-dimensional lumped kinematic storage solver with a 14-feature serverless edge neural surrogate, Cloudflare Workers, and an LLM reasoning gate.

- **Production Frontend (Cloudflare Pages):** `https://floodlock.pages.dev`
- **Core 1: Master Gateway:** `https://floodlock-backend.dakshdahore1995.workers.dev`
- **Core 2: Standby Gateway:** `https://floodlock-backend-standby.dakshdahore1995.workers.dev`
- **Mirror Alpha:** `https://floodlock-backend.dahoremugdha.workers.dev`
- **Mirror Beta:** `https://floodlock-backend.dakshdadafit.workers.dev`
- **Mirror Gamma:** `https://floodlock-backend.lanternmech.workers.dev`
- **Core 3: Dedicated User Click Processor:** `https://floodlock-click-processor.dakshdahore1995.workers.dev`
- **Core 4: Neural 14F Tensor Core:** `https://floodlock-core-neural.dakshdahore1995.workers.dev`
- **Cores 5–11: 7 Continental Hydrological Shards:** `floodlock-shard-{asia-south, asia-east, europe-west, europe-med, north-america, south-america, africa-oceania}.dakshdahore1995.workers.dev`
- **Master Offline Verification Pack:** `floodlock_v3_production_complete.zip` (Pure human-readable source code; zero precompiled binaries, zero `.pt`/`.pth` weights, zero `.mp4` video files, zero `.env` files)

---

### 2. Implementation & Defense Reference

Please audit the implementation against the following specifications:

#### Finding 1: Life-Safety Floor Overwrites Benign Dismissal Text
- **Files:** `floodlock_backend_cloudflare/src/ai_resilience.js`, `src/index.js`, `src/click_processor.js`
- **Verification:**
  1. Inspect `normalizeTacticalPayload()` (`ai_resilience.js:58-120`): When `isPhysicalHazard === true`, actionable fields (`tactical_civic_advisory`, `safe_evacuation_corridors`, `danger_zone_perimeter`, `impassable_infrastructure`, `nearest_open_hospital`) strictly come from `fallbackObj` (deterministic emergency SOP). AI models cannot talk around the floor with polite or evasive language.
  2. In `index.js:1877`, `status: "ALL_CLEAR"` lives exclusively in `index.js` and strictly requires `!isPhysicalHazard && !telem.telemetryDegraded`. `click_processor.js` uses `MONITORED_NOMINAL` and never returns `ALL_CLEAR`.
  3. Verified by Unit Tests #5 and #5b in `test/worker.test.mjs`.

#### Finding 2: Open-Meteo Telemetry Slicing, Volumetric Soil Moisture & Degradation Fail-Safe
- **Files:** `floodlock_backend_cloudflare/src/index.js`, `src/click_processor.js`
- **Verification:**
  1. Inspect `fetchLiveTelemetry()` (`index.js:194-275`):
     - `hourly.time` index matching: Matches `current.time` against `hourly.time` (defaulting to 120h = 5 past days).
     - Antecedent rainfall slicing: `r48` slices backward `slice(Math.max(0, currentIdx - 47), currentIdx + 1)`, reading past hours rather than the future forecast tail.
     - Soil moisture conversion: Open-Meteo volumetric water content $\theta$ ($\text{m}^3/\text{m}^3$) is converted to degree of saturation ($S_e = \min(1.0, \max(0.0, \theta / 0.45))$). A volumetric reading of 0.38 $\text{m}^3/\text{m}^3$ evaluates to 84% saturation, reaching the $\ge 0.80$ floor trigger.
     - Timeout & degradation flag: `fetch()` calls enforce `AbortSignal.timeout(4000)`. When meteorological APIs fail or time out, `telemetryDegraded: true` is returned.
  2. Both `index.js` and `click_processor.js` share `decideThreatState()` (`ai_resilience.js:35-56`). On telemetry failure, they emit `threat_level: "ELEVATED_WATCH"` and fail-safe SOP guidance—never `ALL_CLEAR` or `NOMINAL`.
  3. Verified by Unit Tests #10d and #13 in `test/worker.test.mjs`.

#### Finding 3: Anti-Brute-Force OTP Defense (Global Cap + IPv6 /64 Subnet Keying)
- **Files:** `floodlock_backend_cloudflare/src/durable_objects.js`, `src/index.js`
- **Verification:**
  1. Inspect `normalizeClientIp()` (`durable_objects.js:36-80`): Expands compressed IPv6 addresses into 8 groups, lowercases, strips leading zeros, and extracts the first 4 groups as a normalized `/64` subnet key (`::/64`), preventing prefix bypass.
  2. Two-tier lockout in `SecurityStateDO.verifyOtp()` (`durable_objects.js:210-280`):
     - Tier 1 (IP-scoped): 3 failed strikes from any IP/subnet locks that IP for 15 minutes.
     - Tier 2 (Global challenge cap): Total failed attempts across ALL IPs are tracked on `otp_challenges.attempts`. A rotating attacker gets at most 5 guesses per challenge: on the 5th failed attempt globally, the challenge is destroyed (`DELETE FROM otp_challenges`), and the identity is locked globally for 15 minutes (`CHALLENGE_REVOKED`).
  3. Inspect `SecurityStateDO.issueOtp()`: OTP issuance is throttled to at most 3 requests per 10 minutes per identity (`rate_limit_events`).
  4. Inspect Turnstile verification in `index.js:659-692`: Turnstile verification is mandatory in production; missing token returns 403 `BOT_CHALLENGE_REQUIRED`.
  5. Verified by Unit Tests #10b, #10c, #11, and #12 in `test/worker.test.mjs`.

#### Finding 4: Decoupled Secrets, Binaries & Insecure Fallbacks
- **Files:** `floodlock_backend_cloudflare/src/index.js`, `floodlock_frontend/js/config.js`, root directory
- **Verification:**
  1. `verifyAdminAccess()` (`index.js:638-657`) strictly requires a dedicated `ADMIN_SECRET` of length $\ge 32$ and explicitly rejects session JWTs and raw `MASTER_SECRET` bearers.
  2. Personal emails (`@gmail.com`) are removed from source and replaced with `env.FOUNDER_ALERT_EMAIL` and `env.ADMIN_EMAILS`.
  3. The packaged archive contains zero precompiled binaries, zero `.pt`/`.pth` weights, zero `.mp4` video files, and zero `.env` files.
  4. In `getSafeFrontendRedirect()` (`index.js:100-135`), localhost is blocked in production, and destination redirect domains are strictly allowlisted.
  5. Verified by Unit Tests #8, #9, #10, and #10e in `test/worker.test.mjs`.

#### Finding 5: Parameter Validation & Cache Partitioning
- **Files:** `floodlock_backend_cloudflare/src/index.js`, `src/click_processor.js`, `src/ai_resilience.js`
- **Verification:**
  1. In `click_processor.js` and `index.js`, custom query overrides (`r0`, `r48`, `soil_sat`, `tide`) are validated as finite non-negative numbers.
  2. Custom user query overrides enforce `skipCache: true`, preventing user parameters from poisoning shared KV cache entries.
  3. Cache keys partition on physical hazard state (`ai_resilience.js:175-195`), and any cache read is unconditionally re-normalized against the live physical floor.
  4. Verified by Unit Test #6 in `test/worker.test.mjs`.

#### Finding 6: Scientific Model Scope & Honest Performance Documentation
- **Files:** `trainer/README.md`, `FLOODLOCK_MASTER_VERIFICATION_SPEC.md`, `data/gauge_cases.csv`, `scripts/eval_real_gauges.py`
- **Verification:**
  1. Simulator classification: Classified accurately as a **Zero-Dimensional Lumped Kinematic Storage Model** coupling Green-Ampt infiltration with Manning discharge.
  2. Neural surrogate role: The 14-feature multi-head MLP emulates the 0D lumped simulator. On synthetic holdout sequences (`X_val`), depth MAE is **3.96 cm** against the lumped simulator's own outputs, not against real floods.
  3. Real historical gauge evaluation: Evaluated offline via `scripts/eval_real_gauges.py` on `data/gauge_cases.csv` across 6 verified historical records (Mumbai 2005, Valencia 2024, Zhengzhou 2021, Dubai 2024, Jeddah 2022, Sahara Control), yielding a Mean Absolute Error of **75.34 cm**.
  4. Life-safety floor necessity: The model can under-predict 2D canyon floods (e.g. Valencia: 225 cm observed vs ~22 cm lumped). Safety decisions are therefore driven by the deterministic rainfall and surge floor.

---

### 3. Known Limitations
1. **Targeted OTP Lockout (Availability Trade-off)**: Because the global failure cap revokes a challenge and locks an identity after 5 failed attempts across all IPs, an attacker who knows a target user's email address can intentionally submit 5 incorrect OTP codes to lock that victim's email for 15 minutes. This is a known trade-off to strictly prevent brute-force authentication.
2. **0D Lumped Hydrology Scope**: The lumped numerical solver and surrogate model cannot resolve 2D hydrodynamic flow routing, localized street depression gradients, or channel constriction funneling. Life-safety alerts therefore rely on the deterministic rainfall and surge floor rather than uncalibrated depth estimates.
3. **Offline Sandbox Test Scope**: The offline test suite verifies cryptographic primitives, Durable Object SQLite logic, physics conservation, and neural surrogate tensor operations without network access. Live edge workers, multi-account cluster routing, Groq LPU API latency, and real Resend email delivery require public network connectivity and were not tested in the offline sandbox.

---

### 4. Verification Commands for Zero-Network Environments

```bash
# 1. Master Zero-Network Offline Audit Suite (100% Pass in <1s)
# Verifies 10 landmark benchmarks, 7 conservation unittests, and 18 worker tests
python3 scripts/verify_offline_audit_suite.py

# 2. Standalone Physics Conservation Test Suite (7/7 Pass in 0.014s)
python3 physics/test_physics_conservation.py

# 3. Standalone Node.js WebCrypto & Serverless Worker Test Suite (18/18 Pass in 0.30s)
cd floodlock_backend_cloudflare && node --test test/worker.test.mjs

# 4. Real Historical Gauge Reproducibility Evaluation (MAE: 75.34 cm)
python3 scripts/eval_real_gauges.py

# 5. Endpoint Consistency Check across Frontend & Documentation
python3 scripts/check_endpoints.py
```

---

### 5. Required Output Format
Deliver an uncompromising, evidence-based score out of 100 with:
1. **Distributed Cluster & Parallel Sharding (Pillars 1, 3):** /25
2. **Adversarial AI Resilience & Life-Safety Floor (Pillars 2, 4):** /25
3. **Mathematical Hydrology & Telemetry (Pillars 5, 6):** /25
4. **Cryptographic Zero-Trust, Admin Decoupling & Security (Pillars 7, 8):** /25
5. **Final Verdict:** State clearly whether FloodLock v3.2.0 earns a definitive **GREEN FLAG (GO FOR GLOBAL PRODUCTION)** or **RED FLAG**, supported by specific line citations for every verification point.
```
