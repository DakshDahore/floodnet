# FloodLock v3.2.0-Gold — Master Evaluator Audit Prompt for Gemini & Claude

Upload `floodlock_v3_2_gold_pack.zip` to Google Gemini (or Anthropic Claude) and paste the exact prompt below:

```markdown
You are acting as the Chief Scientist, Principal Cryptographer, and Senior Infrastructure Security Auditor conducting an exhaustive, uncompromising engineering audit of "FloodLock v3.2.0-Gold".

### 1. Executive Summary & Founder Intent
FloodLock is a commercial planetary flood intelligence platform founded by Daksh (14 years old). The platform predicts urban, riverine, flash, and coastal tidal inundations globally within milliseconds, coupling a first-principles numerical PDE hydrology simulator (Engine 1) with an ultra-low-latency 14-feature V8 edge neural surrogate (Engine 2) and a 3-tier distributed tactical reasoning pipeline.

- **Primary Edge Node:** `https://floodlock-backend.dakshdahore1995.workers.dev`
- **Hot Standby Edge Node:** `https://floodlock-backend-standby.dakshdahore1995.workers.dev`
- **Verification Package:** `floodlock_v3_2_gold_pack.zip`

---

### 2. Audit Scope & Verification Pillars
Perform an exhaustive, line-by-line inspection across the 7 engineering pillars of the attached codebase:

#### Pillar 1: Planetary Flood Telemetry & Real-Time ECMWF Copernicus GloFAS Feeds
- **Files:** `cloudflare_worker/src/index.js` (lines 40–180), `floodlock_frontend/index.html` (lines 280–420)
- **Zero Mock / Zero Fake Policy:** Verify that flood alerts are driven by live, real-world river basin discharge telemetry via the ECMWF Copernicus GloFAS / Open-Meteo Flood API—never hardcoded alert strings or static arrays.
- **Monitored Planetary Basins:** Confirm active real-time monitoring across 15 major global river catchments (Danube, Rhine, Mississippi, Nile, Amazon, Mekong, Ganges-Brahmaputra, Yangtze, Ulhas, Indus, etc.).
- **90-Day Continuous Telemetry:** Verify `/api/flood/telemetry` retrieves continuous 90-day time-series data (60 days observed historical discharge + 30 days forecast discharge at m³/s) with automated gauge fallback for coastal grid points.
- **Client-Side Tactical Hydrograph:** Verify that `floodlock_frontend/index.html` renders interactive 90-day hydrograph curves using Chart.js, plotting observed vs. forecast discharge against critical flood thresholds with seamless panning and zooming.

#### Pillar 2: Geolocation Flood Radius Scanner (≤ 150 km Perimeter Engine)
- **Files:** `cloudflare_worker/src/index.js` (lines 190–260), `floodlock_frontend/index.html`
- **Haversine Geodesic Math:** Verify that `GET /api/flood/radius-check?lat=...&lon=...&radius_km=150` computes great-circle distances across all global river catchments using exact spherical geodesics:
  d = 2R * arcsin(sqrt(sin²(Δφ/2) + cos φ₁ * cos φ₂ * sin²(Δλ/2)))
- **Dynamic Risk Categorization:** Verify that danger ratings (`CRITICAL`, `ELEVATED`, `NOMINAL`) dynamically match proximity and discharge ratios (Q_current / Q_mean), sounding audible audio synthesis alarms and visual radar pulses on the frontend map deck.

#### Pillar 3: Mathematical Hydrology & Mass Conservation
- **File:** `physics/floodlock_physics_simulator.py` & `physics/test_physics_conservation.py`
- **Adaptive CFL Sub-stepping:** Verify the 36-step (Δt = 600 s, 6.0h horizon) solver with dynamic adaptive CFL sub-stepping (`min_substeps = 12`, scaling up to `120`).
- **Infiltration & Hydrostatic Equilibrium:** Confirm supply-limited Green-Ampt infiltration draws strictly from `available_m = h + inflow_m`, and Torricelli submerged orifice backwater caps strictly at hydrostatic equilibrium H_tide - Z_invert.
- **Global Mass Conservation:** Confirm Σ(h_{t+dt} - h_t) = Σ(P - I - Q)Δt with mass residual < 1.20 × 10⁻¹⁴ m across all 7 rigorous test regimes (Dubai cloudburst, Valencia flash flood, extreme 10m storm surge, Sahara zero-rain, etc.).

#### Pillar 4: Cryptographic Zero-Trust Core & Atomic State Rollback
- **Files:** `cloudflare_worker/src/crypto_utils.js`, `cloudflare_worker/src/durable_objects.js`
- **Domain-Separated HKDF:** Verify HKDF-SHA256 isolating keys for `identity-hash`, `otp-hash`, `session-jwt-hs256`, and `aes-256-gcm-pii`.
- **Authenticated Encryption:** Verify WebCrypto AES-256-GCM with fresh 96-bit random IVs and mandatory Additional Authenticated Data (`identityHash`).
- **Atomic OTP State Rollback:** Verify that if SMS/Email OTP dispatch encounters an upstream failure (e.g., HTTP 502), `SecurityStateDO.rollbackOtp()` clears the pending challenge to prevent cooldown trapping while preserving rolling brute-force abuse strikes.
- **Privacy Assurance:** Confirm that raw OTP codes are strictly isolated from telemetry alerts and never leaked to founder notifications.

#### Pillar 5: Commercial Inquiries, Dual-Dispatch EmailJS & Founder Verification
- **Files:** `cloudflare_worker/src/index.js`, `cloudflare_worker/wrangler.jsonc`, `floodlock_frontend/index.html`
- **Dual-Layer Email Delivery:** Verify that custom GPay inquiries, founder alerts, and verification notifications utilize dual-layer dispatch: primary via client browser EmailJS SDK (`window.emailjs.send`) with transparent edge worker API failover (`fetch('https://api.emailjs.com/api/v1.0/email/send')`).
- **Configuration Hygiene:** Confirm `EMAILJS_SERVICE_ID = "service_8yw2mtw"` is properly bound without leaking private keys.
- **Founder Command Center:** Verify the administrative verification queue for `dakshdahore.d@gmail.com`:
  - Pending user verification requests enter a persistent admin list.
  - Clicking approval triggers an instant atomic KV plan upgrade (`pro` or `ultra`) with re-encrypted AES-256-GCM credentials and clears the user from the queue.
  - Complete elimination of hardcoded legacy personal UPI handles.

#### Pillar 6: Strongly Consistent Edge State & Durable Objects
- **Files:** `cloudflare_worker/src/durable_objects.js`, `cloudflare_worker/src/ai_resilience.js`
- **SecurityStateDO:** Verify atomic 3-strike lockout (`HTTP 403`), true sliding-window 60 req/min rate limiter with `DELETE ... AND ts <= ?`, and SQLite `alarm()` garbage collection.
- **BillingStateDO:** Verify actor-sharded SQLite Durable Objects (`bill:${userId}`), separating UTC daily quotas from monotonic lifetime quotas, and automatic settlement of expired 5-day hold windows.
- **Life-Safety AI Guard:** Verify that AI reasoning models (Groq LPU Tier 1, Gemini Tier 2) can never downgrade verified physical warnings (`CRITICAL`/`EXTREME` → `NOMINAL`).

#### Pillar 7: Automated Verification Suite Execution
Run the verification suites contained in the package:
```bash
# 1. Physics Conservation Suite (7/7 tests)
python3 physics/test_physics_conservation.py

# 2. Offline WebCrypto & Billing Unit Tests
node --test cloudflare_worker/test/worker.test.mjs

# 3. Live 18-Vector Edge Penetration Suite
python3 security/security_redteam_harness_v3_2.py https://floodlock-backend-standby.dakshdahore1995.workers.dev
```

---

### 3. Required Output Format
Deliver an uncompromising, evidence-based score out of 100 with:
1. **Mathematical & Hydrological Integrity (Pillars 1–3):** /30
2. **Cryptographic & Edge State Zero-Trust (Pillars 4, 6):** /25
3. **Operational Commercial Resilience & Dispatch (Pillars 5):** /25
4. **Verification & Attack Penetration Defeat (Pillar 7):** /20
5. **Final Verdict:** State clearly whether FloodLock v3.2.0-Gold is **GO FOR GLOBAL PRODUCTION** or **NO-GO**, accompanied by specific line citations for every claim.
```
