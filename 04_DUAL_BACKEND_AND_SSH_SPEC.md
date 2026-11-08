``markdown
# 04 — DUAL BACKENDS (LOCAL MSI1 + CLOUD FALLBACK), LOCKED M2M LLM & NATIVE SSH
**Target Directories:** `floodlock_backend_local/`, `floodlock_backend_cloud/`, `scripts/`

---

## 1. BACKEND 1: ON-PREM SERVER (`floodlock_backend_local/` — MSI1 / Arch Linux)
Runs on port `8000` (`uvicorn app:app --host 0.0.0.0 --port 8000`).

### Required Endpoints:
1. `GET /health`:
   - Returns `{ "status": "ONLINE", "node": "LOCAL_MSI1_SERVER", "device": "cuda/cpu", "model_737_loaded": true, "model_209_loaded": true, "ollama_status": "READY (qwen2.5:0.5b)", "holdout_mae_min": ... }`.
2. `GET /api/live-mumbai`:
   - Queries Open-Meteo Forecast API (`https://api.open-meteo.com/v1/forecast?latitude=19.0160&longitude=72.8430&current=precipitation,rain,surface_pressure,wind_speed_10m,wind_direction_10m`) and Open-Meteo Marine API (`https://marine-api.open-meteo.com/v1/marine?latitude=19.0065&longitude=72.8165&current=wave_height&hourly=sea_level_height_msl`).
   - If the user has provided an `OPENWEATHER_API_KEY` in `.env` or request headers, cross-verifies wind and pressure readings.
   - Runs full physics harmonizer + 209 & 737 neural models and returns complete telemetry JSON.
3. `GET /api/scenarios/{scenario_id}`:
   - Supports `july2023`, `july2005`, `nominal`, and `unseen_sample` (loads a random row from `holdout_unseen_telemetry.csv` and compares True Physics ETA vs. Neural Predicted ETA so the operator can audit generalization live in the UI).
4. `POST /api/telemetry`:
   - Accepts `{ rain_instant, rain_1hr, pressure_hpa, tide_astro_m, wind_speed_ms, wind_dir_deg, subsidence_mm_yr }`.
   - Computes:
     - `v_onshore`, `wind_surge_m`, `baro_surge_m`, `effective_tide_m`
     - `outfall_choke_pct` (`0%` to `100%` at `3.0m MSL` Love Grove invert)
     - `q_drain_mm_hr`, `net_inflow_mm_hr`, `simulated_water_depth_m`
     - `eta_209_minutes` and `eta_737_minutes`
     - `routing`: Dynamic A* status (`SURFACE_OPEN` if depth `< 0.30m`, else `REROUTE_DADAR_TT_VIADUCT_8_5M`).
5. `POST /api/dispatch` (**STRICTLY LOCKED M2M LLM ENDPOINT**):
   - **SECURITY RULE:** Rejects any payload containing arbitrary user chat strings. Accepts ONLY validated numeric telemetry state from the system.
   - Constructs a strict M2M system prompt and invokes local Ollama (`http://127.0.0.1:11434/api/generate`, `model: "qwen2.5:0.5b"`, `stream: false`) to generate a 4-part structured JSON/Markdown **MCGM F-South Ward Emergency Directive**:
     - `alert_code`: `GREEN_NOMINAL` | `AMBER_WATCH` | `RED_WARNING` | `CRITICAL_HYDRAULIC_LOCK`
     - `sluice_and_pump_order`: Specific operational command for Love Grove Sluice Gates and Pramod Mahajan Sump Pumps.
     - `evacuation_route_order`: Specific traffic/ambulance directive for Hindmata Underpass vs. Dadar TT Elevated Viaduct (`+8.5m MSL`) toward KEM Hospital.
     - `citizen_safety_bulletin`: Concise public safety warning.
   - If Ollama is offline on the host machine, automatically falls back to a deterministic institutional protocol template so the endpoint never returns a 500 error.

---

## 2. BACKEND 2: ONLINE CLOUD FALLBACK (`floodlock_backend_cloud/`)
- Designed to be deployed online (Render / Railway / Fly.io / Docker) so the Netlify/Cloudflare frontend always has a live online backend even when the `MSI1` laptop is powered off.
- Uses lightweight pure `numpy` matrix multiplication loaded from `data/weights_backend.json` (zero heavy PyTorch/CUDA bloat so it deploys on free 512MB RAM cloud instances in `<30 seconds`).
- Implements the exact same endpoints (`/health`, `/api/live-mumbai`, `/api/scenarios/{id}`, `/api/telemetry`, `/api/dispatch`).
- Frontend `config.js` includes automatic failover: tries `MSI1_BACKEND_URL` (or `localhost:8000`), and if unreachable within `1500ms`, seamlessly switches to `CLOUD_BACKEND_URL` and local `BrowserEdgeMLP`.

---

## 3. NATIVE OPENSSH & CLOUDFLARE TUNNEL SCRIPTS (`scripts/`)
1. `scripts/deploy_to_msi_ssh.sh`:
   - Uses standard built-in OpenSSH (`ssh` and `scp`) to connect to `yuvamps1@<MSI_IP>`.
   - Copies `data/`, `floodlock_trainer/`, and `floodlock_backend_local/` to `C:\floodlock\` on `MSI1`.
   - Triggers remote training or backend startup over native SSH without requiring any third-party remote desktop apps.
2. `scripts/start_cloudflare_tunnel.bat` & `.sh`:
   - Runs `cloudflared tunnel --url http://localhost:8000` to generate an instant `https://*.trycloudflare.com` public URL for the `MSI1` backend whenever remote internet access is needed (e.g., from Delhi).
