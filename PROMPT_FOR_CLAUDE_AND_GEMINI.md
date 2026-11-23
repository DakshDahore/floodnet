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

### 2. Audit Scope & Verification Pillars
Perform an exhaustive inspection across all 8 engineering pillars, including the 5 resolved audit findings:

#### Pillar 1: Distributed 10-Core Cloudflare Architecture & Sharded Work Division
- **Files:** `floodlock_backend_cloudflare/src/index.js` (or `cloudflare_worker/src/index.js`), `src/click_processor.js`, `src/neural_core_worker.js`, `src/shard_worker.js`, `src/planetary_grid.js`
- **Zero-Contention Click Core:** Verify that interactive user clicks and point queries are served by a dedicated isolate (`floodlock-click-processor`) with <50ms edge latency.
- **In-Memory Service Bindings:** Verify that the Master Gateway aggregates all 7 continental shards and the Neural 14F tensor core over zero-cost in-memory V8 service bindings without public network egress.
- **Multi-Account Failover Pool:** Verify client-side and gateway automated failover across 4 distinct Cloudflare accounts (`lanternmech`, `dahoremugdha`, `dakshdadafit`, `dakshdahore1995`).

#### Pillar 2: Adversarial Groq Verification Gate & Civil Defense Safety Floor (Finding 3 Resolved)
- **Files:** `floodlock_backend_cloudflare/src/ai_resilience.js`, `src/click_processor.js`, `src/index.js`, `floodlock_frontend/index.html`
- **Deterministic Physical Hazard Floor:** In `ai_resilience.js`, inspect `isDeterministicPhysicalHazard()`. Verify that when physical telemetry indicates severe deluge (R0 ≥ 15 mm/h, R48 ≥ 50 mm, surge ≥ 1.5m, soilSat ≥ 80%, h1 ≥ 15 cm, or Q ≥ 150 m³/s), the AI model is STRICTLY FORBIDDEN from downgrading the alarm.
- **Fail-Safe Invariant:** Even if Groq/Gemini returns `threat_verified: false`, hallucinates, times out, or errors, the deterministic safety floor overrides the AI (`action_taken: OVERRIDDEN_BY_PHYSICAL_SAFETY_FLOOR`), forcing `CRITICAL_INUNDATION` and outputting safe evacuation corridors and elevated trauma hospital routes.
- **Legitimate False Alarm Pruning:** AI downgrade is ONLY allowed when physical telemetry is genuinely benign (e.g. R0 = 0, dry soil) where the neural net had a borderline false alarm.

#### Pillar 3: Adaptive Mesh Refinement (AMR) & Full Earth Spatial Quadtree
- **Files:** `floodlock_backend_cloudflare/src/planetary_grid.js`, `floodlock_frontend/index.html`
- **Planetary Coverage:** Verify that AMR quadtrees partition the entire planet, dynamically subdividing high-risk coastal and riverine cells from ~200km macro-sectors down to 10km and 2km local tiles while pruning arid interiors in O(1) time.
- **Priority Queue Execution:** Verify that planetary workers process red hotspot clusters first, followed by elevated amber watch cells, and finally nominal blue cells.

#### Pillar 4: Frontend Map Camera & 1–10km Resolution Zoom
- **File:** `floodlock_frontend/index.html`
- **Precise Zoom Scaling:** Verify that clicking on any quadtree box, red hotspot, active flood marker, or arbitrary pinpoint on Earth triggers `mapInstance.flyTo({ center, zoom: 12.8, pitch: 35 })`, focusing the user immediately into the 1–10km ground scale (~3.5km visible span).

#### Pillar 5: Real-Time ECMWF Copernicus GloFAS & Open-Meteo Ingestion
- **Files:** `floodlock_backend_cloudflare/src/click_processor.js`, `src/index.js`, `floodlock_frontend/index.html`
- **Zero Mock Policy:** Verify all flood warnings and river discharge time-series are computed from live ECMWF GloFAS and Open-Meteo REST APIs — never fabricated arrays or static fixtures.
- **90-Day Continuous Discharge Hydrograph:** Confirm `/api/flood/telemetry` delivers continuous 60-day historical + 30-day projected river discharge hydrographs rendered client-side with Chart.js.

#### Pillar 6: Mathematical Hydrology & Mass Conservation
- **Files:** `floodlock_physics_simulator.py` (and `physics/floodlock_physics_simulator.py`), `test_physics_conservation.py` (and `physics/test_physics_conservation.py`)
- **Adaptive CFL Sub-stepping:** Verify the 36-step solver (Δt = 600 s, 6.0h horizon) with dynamic adaptive CFL sub-stepping (12 ≤ substeps ≤ 120).
- **Strict Conservation:** Confirm Σ(h_{t+Δt} - h_t) = Σ(P - I - Q)Δt with mass residual < 1.20 × 10⁻¹⁴ m across all test regimes.

#### Pillar 7: Cryptographic Security, Admin Decoupling & OAuth Defense (Findings 1, 2, 4 Resolved)
- **Files:** `floodlock_backend_cloudflare/src/crypto_utils.js`, `src/durable_objects.js`, `src/index.js`
- **Dedicated Admin Secret (Finding 4):** Verify in `verifyAdminAccess()` that `ADMIN_SECRET` is strictly decoupled from `MASTER_SECRET`. Confirm that bearer tokens matching `MASTER_SECRET` directly are REJECTED with HTTP 403 (`NOT_ADMIN`), completely eliminating root cryptographic secret exposure.
- **OAuth Open Redirect Defense (Finding 1):** Verify in `src/index.js` that `getSafeFrontendRedirect(rawOrigin, env)` validates and sanitizes all callback redirect URLs against a strict whitelist. Injected attacker origins (`https://evil-attacker.com`) are stripped, preventing session token theft.
- **Strict Email Verification (Finding 2):** Verify that Google OAuth enforces `verified_email === true` and GitHub OAuth strictly queries `/user/emails` for `verified === true` (never accepting unverified profile emails or `emails[0]`), preventing unverified admin privilege escalation.
- **Domain-Separated HKDF:** Verify HKDF-SHA256 isolating keys for `identity-hash`, `otp-hash`, `session-jwt-hs256`, and `aes-256-gcm-pii`.
- **Atomic OTP State Rollback:** Confirm `SecurityStateDO.rollbackOtp()` clears challenges on delivery failures (HTTP 502).

#### Pillar 8: Supply Chain Integrity & Verification Suite Execution (Finding 5 Resolved)
- **Zero Precompiled Binaries (Finding 5):** The package contains ONLY pure human-readable source code. The unverified `cloudflared` binary has been removed.
- Run the automated verification suites:
```bash
# 1. Complete Cluster, Security, Admin Isolation & Groq Gate Suite (21/21 GREEN FLAGS)
python3 scripts/verify_10core_cluster_and_groq_gate.py

# 2. Physics Conservation Suite (7/7 Solvers OK in 0.017s)
python3 physics/test_physics_conservation.py

# 3. Offline WebCrypto & Billing Unit Tests (4/4 Tests OK in 170ms)
cd floodlock_backend_cloudflare && node --test test/worker.test.mjs

# 4. Live 17-Vector Edge Security Red-Team Penetration Suite (17/17 PASSED, 0 FAILURES)
python3 scripts/security_redteam_harness_v3.py
```
Expected output: **100% PASS RATE ACROSS ALL 4 SUITES**.

---

### 3. Required Output Format
Deliver an uncompromising, evidence-based score out of 100 with:
1. **Distributed Cluster & Parallel Sharding (Pillars 1, 3):** /25
2. **Adversarial AI Resilience & Life-Safety Floor (Pillars 2, 4):** /25
3. **Mathematical Hydrology & Telemetry (Pillars 5, 6):** /25
4. **Cryptographic Zero-Trust, Admin Decoupling & Security (Pillars 7, 8):** /25
5. **Final Verdict:** State clearly whether FloodLock v3.2.0-Gold is **GO FOR GLOBAL PRODUCTION** or **NO-GO**, accompanied by specific line citations for every claim.
```
