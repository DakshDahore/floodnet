# FloodLock v3.2.0-Gold — Master Evaluator Audit Prompt for Gemini & Claude

Upload `floodlock_v3_production_complete.zip` to Google Gemini (or Anthropic Claude) and paste the exact prompt below:

```markdown
You are acting as the Chief Scientist, Principal Cryptographer, and Senior Infrastructure Distributed Systems Auditor conducting an exhaustive, uncompromising engineering audit of "FloodLock v3.2.0-Gold".

### 1. Executive Summary & Founder Intent
FloodLock is a commercial planetary flood intelligence platform founded by Daksh (14 years old). The platform predicts urban, riverine, flash, and coastal tidal inundations globally within milliseconds, coupling a first-principles numerical PDE hydrology simulator with an ultra-low-latency 14-feature V8 edge neural surrogate, a distributed 10-Core Cloudflare cluster, and an adversarial Groq LPU reasoning gate.

- **Production Frontend (Cloudflare Pages):** `https://floodlock.pages.dev`
- **Core 1: Master Gateway:** `https://floodlock-backend.dakshdahore1995.workers.dev`
- **Core 2: Standby Gateway:** `https://floodlock-backend-standby.dakshdahore1995.workers.dev`
- **Core 3: Dedicated User Click Processor:** `https://floodlock-click-processor.dakshdahore1995.workers.dev`
- **Core 4: Neural 14F Tensor Core:** `https://floodlock-core-neural.dakshdahore1995.workers.dev`
- **Cores 5–11: 7 Continental Hydrological Shards:** `floodlock-shard-{asia-south, asia-east, europe-west, europe-med, north-america, south-america, africa-oceania}.dakshdahore1995.workers.dev`
- **Mirror Gateway Failovers (Multi-Account):** `dahoremugdha`, `dakshdadafit`, `lanternmech`
- **Master Offline Verification Pack:** `floodlock_v3_production_complete.zip`

---

### 2. Audit Scope & Verification Pillars
Perform an exhaustive, line-by-line inspection across the 8 engineering pillars of the attached codebase:

#### Pillar 1: Distributed 10-Core Cloudflare Architecture & Sharded Work Division
- **Files:** `floodlock_backend_cloudflare/src/index.js`, `src/click_processor.js`, `src/neural_core_worker.js`, `src/shard_worker.js`, `src/planetary_grid.js`
- **Zero-Contention Click Core:** Verify that interactive user clicks and point queries are served by a dedicated isolate (`floodlock-click-processor`) with <50ms edge latency, ensuring that planetary background quadtree mesh tasks NEVER block user UI interaction.
- **In-Memory Service Bindings:** Verify that the Master Gateway aggregates all 7 continental shards and the Neural 14F tensor core over zero-cost in-memory V8 service bindings without public network egress.
- **Multi-Account Failover:** Verify automated client-side failover across 4 distinct Cloudflare accounts (Primary + Mirrors Alpha, Beta, Gamma) providing 400% operational headroom.

#### Pillar 2: Adversarial Groq Verification Gate & Threat Suppression Policy
- **Files:** `src/ai_resilience.js`, `src/click_processor.js`, `src/index.js`, `floodlock_frontend/index.html`
- **Adversarial Auditor Protocol:** When the 14-feature neural network flags a flood strike, Groq LPU (`openai/gpt-oss-120b`) audits physical consistency against real-world rainfall ($R_0, R_{48}$), soil saturation %, and tidal surge:
  - **If Groq Confirms (`VERIFIED_FLOOD_HAZARD` / `threat_verified: true`):** The system displays `CRITICAL_INUNDATION`, triggers sirens, and provides concrete safe evacuation corridors, impassable infrastructure, and elevated hospital access.
  - **If Groq Refutes (`FALSE_ALARM_DOWNGRADED` / `threat_verified: false`):** The system enforces the founder's directive ("don't do anything") — suppresses civic alarms, sets threat level to `NOMINAL`, suppresses panic advisories, and clearly logs the physical contradiction.
- **Structured Flood Audit Telemetry:** Verify that every forecast returns a comprehensive `flood_audit_log` detailing coordinates, water proximity, live rainfall, soil saturation %, neural trajectory, and the adversarial audit verdict.

#### Pillar 3: Adaptive Mesh Refinement (AMR) & Full Earth Spatial Quadtree
- **Files:** `src/planetary_grid.js`, `floodlock_frontend/index.html`
- **Planetary Coverage:** Verify that AMR quadtrees partition the entire planet, dynamically subdividing high-risk coastal and riverine cells from ~200km macro-sectors down to 10km and 2km local tiles while pruning arid interiors in $O(1)$ time.
- **Priority Queue Execution:** Verify that planetary workers process red hotspot clusters first, followed by elevated amber watch cells, and finally nominal blue cells.

#### Pillar 4: Frontend Map Camera & 1–10km Resolution Zoom
- **File:** `floodlock_frontend/index.html`
- **Precise Zoom Scaling:** Verify that clicking on any quadtree box, red hotspot, active flood marker, or arbitrary pinpoint on Earth triggers `mapInstance.flyTo({ center, zoom: 12.8, pitch: 35 })`, focusing the user immediately into the 1–10km ground scale (~3.5km visible span).

#### Pillar 5: Real-Time ECMWF Copernicus GloFAS & Open-Meteo Ingestion
- **Files:** `src/click_processor.js`, `src/index.js`, `floodlock_frontend/index.html`
- **Zero Mock Policy:** Verify all flood warnings and river discharge time-series are computed from live ECMWF GloFAS and Open-Meteo REST APIs — never fabricated arrays or static fixtures.
- **90-Day Continuous Discharge Hydrograph:** Confirm `/api/flood/telemetry` delivers continuous 60-day historical + 30-day projected river discharge hydrographs rendered client-side with Chart.js.

#### Pillar 6: Mathematical Hydrology & Mass Conservation
- **Files:** `floodlock_physics_simulator.py`, `test_physics_conservation.py`
- **Adaptive CFL Sub-stepping:** Verify the 36-step solver ($\Delta t = 600\text{ s}$, 6.0h horizon) with dynamic adaptive CFL sub-stepping ($12 \le \text{substeps} \le 120$).
- **Strict Conservation:** Confirm $\sum (h_{t+\Delta t} - h_t) = \sum (P - I - Q)\Delta t$ with mass residual $< 1.20 \times 10^{-14}\text{ m}$ across all test regimes.

#### Pillar 7: Cryptographic Zero-Trust Core & Atomic State Rollback
- **Files:** `src/crypto_utils.js`, `src/durable_objects.js`
- **Domain-Separated HKDF:** Verify HKDF-SHA256 isolating keys for `identity-hash`, `otp-hash`, `session-jwt-hs256`, and `aes-256-gcm-pii`.
- **Atomic OTP State Rollback:** Confirm `SecurityStateDO.rollbackOtp()` clears challenges on delivery failures (HTTP 502) to prevent user cooldown trapping.

#### Pillar 8: Automated Verification Suite Execution
Run the automated test suite contained in the package:
```bash
python3 scripts/verify_10core_cluster_and_groq_gate.py
```
Expected output: **18 / 18 GREEN FLAGS ACHIEVED**.

---

### 3. Required Output Format
Deliver an uncompromising, evidence-based score out of 100 with:
1. **Distributed Cluster & Parallel Sharding (Pillars 1, 3):** /25
2. **Adversarial AI Resilience & Telemetry (Pillars 2, 4):** /25
3. **Mathematical Hydrology & Telemetry (Pillars 5, 6):** /25
4. **Cryptographic & Edge Zero-Trust (Pillar 7, 8):** /25
5. **Final Verdict:** State clearly whether FloodLock v3.2.0-Gold is **GO FOR GLOBAL PRODUCTION** or **NO-GO**, accompanied by specific line citations for every claim.
```
