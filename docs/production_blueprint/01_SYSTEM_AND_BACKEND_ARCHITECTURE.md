# 🏗️ FLOODLOCK HIGH-AVAILABILITY SYSTEM & BACKEND ARCHITECTURE
**Tier**: 100% Free-Tier High-Availability Multi-Cloud Topology  
**Target Performance**: Sub-200ms Global Edge Response, Zero-Cost Base Operational Overhead.

---

## 1. High-Level Multi-Cloud Topology

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 GLOBAL CITIZEN / DEV CLIENT            │
                  │   Desktop / Mobile PWA • Apple-Style Liquid Dock       │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         ┌──────────────────────────┐                   ┌──────────────────────────┐
         │     CLOUDFLARE PAGES     │                   │    CLOUDFLARE WORKERS    │
         │  Ultra-Fast Static Edge  │                   │    Edge API Gateway      │
         │  Netlify Mirror Backup   │                   │  API Key & Rate Limiter  │
         └──────────────────────────┘                   └─────────────┬────────────┘
                                                                      │
                      ┌───────────────────────────────────────────────┴─────────────────┐
                      ▼                                                                 ▼
         ┌──────────────────────────┐                                     ┌──────────────────────────┐
         │     SUPABASE (POSTGRES)  │                                     │     COMPUTE ENGINE POOL  │
         │  • Multi-OAuth (Google)  │                                     │  • Hugging Face Spaces   │
         │  • API Keys & Rate Usage │                                     │  • Dell Mint Server      │
         │  • UPI Purchase Ledger   │                                     │    (Cloudflare Tunnel)   │
         │  • 15TB Cold Drive Sync  │                                     │  • ONNX Client WebGL     │
         └──────────────────────────┘                                     └──────────────────────────┘
```

---

## 2. Core Architectural Subsystems

### A. Edge Routing & Gateway Layer (Cloudflare Workers)
* **Zero Cold-Start**: Runs on V8 isolates worldwide in <15ms.
* **Quota & Key Verification**: Intercepts `Authorization: Bearer fl_live_...`, validates against Supabase edge cache, decrements daily quota.
* **Rate-Limiting**: Enforces tier limits (Free: 50 req/day; Premium: 2,500 req/day; Ultra: 15,000 req/day).
* **Failover Redundancy**: If Primary Worker endpoint suffers network degradation, client automatically shifts to secondary edge mirror on Netlify Functions.

### B. Database & Storage Subsystem (Supabase Free Tier + 15TB Drive)
* **PostgreSQL Schema**:
  * `profiles`: `id, email, role, tier, created_at, age_verified`
  * `api_keys`: `id, user_id, key_hash, key_prefix, tier, daily_quota, usage_today, active`
  * `purchases`: `id, user_id, amount_inr, tier, upi_ref, payment_status, metadata, expires_at, created_at`
  * `user_flood_reports`: `id, user_id, lat, lon, water_depth_est, verification_score, status, photo_url`
* **Large File Storage**: Open-source models (1B–3B parameter GGUF/ONNX) and large historical simulation datasets are hosted on Supabase Storage + mirror-linked to Daksh's 15TB storage cloud.

### C. Global Hydrology & Weather Grid Architecture
To process weather for the entire planet without exhausting free compute:
1. **Coarse Macro Grid (0.25° $\approx$ 25 km)**:
   * Ingests global GFS / ECMWF / Open-Meteo telemetry across major latitude/longitude zones.
2. **Spatial Anomaly Triggering**:
   * An edge worker runs a lightweight filter:
     $$\text{Trigger Condition} = (\text{Rain} > 15\text{ mm/hr}) \lor (\text{CAPE} > 1200\text{ J/kg}) \lor (\text{Surge} > 0.7\text{m})$$
3. **Micro-Basin Deep Inference (1 km resolution)**:
   * Only active threat zones trigger the deep temporal neural network to compute street-level street inundation and outfall backflow.

### D. Crowdsourced RLHF & Truth Protocol
* Citizens can submit local water-logging reports.
* **Secondary Trust Filter**: The system **never** accepts user reports blindly. An automated spatial verification algorithm checks the nearest atmospheric station, elevation contour, and rainfall radar:
  * If plausible $\implies$ report is accepted, elevation heatmap updates, and case is queued for RLHF model retraining.
  * If contradicted by atmospheric physics $\implies$ flagged as anomaly, preventing malicious panic generation.

