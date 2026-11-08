# 00 — MASTER GOVERNANCE & EXECUTION PROTOCOL
**Project:** FloodLock — 3-Tier Urban Flood Intelligence & Hydraulic Backflow Engine  
**Status:** ✅ **COMPLETED & DEPLOYED (Production Live)**  
**Target Precinct:** Mumbai F-South Ward (Hindmata Basin `19.0160° N, 72.8430° E` & Love Grove Outfall `19.0065° N, 72.8165° E`)  
**Workspace Root:** `/home/daksh/Documents/Projects/floodlock`  
**Production URLs:**
- GitHub Pages: https://dakshdahore1995-design.github.io/floodlock/
- Netlify Production: https://floodnet.netlify.app
- Cloudflare Edge Backend (24/7): https://floodlock-backend.dakshdahore1995.workers.dev
- Complete Memory Extraction Pack: `/home/daksh/Documents/Projects/floodlock/floodlock_gemini_complete_memory_pack.zip`

---

## 1. MANDATORY ANTI-HALLUCINATION & ANTI-VIBE-CODING LAWS
You are acting as a Principal Systems Architect, Hydrological ML Engineer, and Staff UI/UX Engineer. Read all 5 `.md` files in this workspace (`00_MASTER_GOVERNANCE.md`, `01_UI_UX_DESIGN_SPEC.md`, `02_HYDROLOGY_AND_CSV_SPEC.md`, `03_NEURAL_NET_TRAINING_SPEC.md`, `04_DUAL_BACKEND_AND_SSH_SPEC.md`) and inspect all uploaded UI reference images in `/home/daksh/Documents/Projects/floodlock/` before writing any code.

**Violation of any of the following 6 rules is an immediate failure:**

1. **ZERO FAKE TRAINING OR MOCKED WEIGHTS:**
   - Never hardcode dummy JSON arrays or use `Math.random()` to simulate neural inference.
   - Never claim a model is trained without executing the actual PyTorch training script in the terminal and displaying the epoch-by-epoch loss on both `train_telemetry.csv` and `holdout_unseen_telemetry.csv`.
2. **MANDATORY API KEY & CONFIG GATE (ASK THE USER):**
   - Never claim "no API keys are required."
   - Before finalizing the 3D map and weather pipelines, pause and ask the operator (Daksh) for:
     - `CESIUM_ION_TOKEN` (for 4K 3D global terrain & OSM building extrusions)
     - `OPENWEATHER_API_KEY` (optional secondary weather verification alongside keyless Open-Meteo REST APIs)
     - `MAPBOX_ACCESS_TOKEN` / `STADIA_API_KEY` (optional, with automatic fallback to keyless CartoDB Dark Matter / Positron monochromatic tiles so the map renders immediately even before keys are entered)
     - `MSI1_SSH_IP` (for native OpenSSH deployment to the Windows compute server)
   - Build a dedicated `[API Keys & Node Config]` modal inside the Web UI (`localStorage` backed + `.env` synced) so the operator can enter, test, or swap keys live in the browser without restarting servers.
3. **NO VIBE-CODED GARBAGE UI:**
   - Strictly implement the 5 human design references detailed in `01_UI_UX_DESIGN_SPEC.md`.
   - Include the **4K Cinematic Hero Entrance** (with high-resolution storm video/shader background, *"ASSISTIVE AI"* serif-italic typography, and system explainer) that transitions smoothly into the **Tactical Crisis Command Deck**.
4. **MANDATORY SCENARIO & SIMULATION MODES:**
   - You must build the 4 operational modes:
     1. `LIVE MUMBAI TELEMETRY` (Real-time Open-Meteo Weather, Wind Vector & Marine Tide APIs)
     2. `JULY 2023 CLOUDBURST` (Historical replay of July 19, 2023 Mumbai flood)
     3. `JULY 2005 CATASTROPHE` (Historical replay of July 26, 2005 944mm disaster)
     4. `MANUAL STRESS SIMULATOR` (60 FPS interactive sliders for Rainfall, Tide, Pressure, Wind Speed, Wind Direction, and Subsidence)
5. **LOCKED MACHINE-TO-MACHINE (M2M) LLM SANDBOX:**
   - The local Ollama `qwen2.5:0.5b` model (~162 tokens/sec) is **strictly for autonomous system use**.
   - **DO NOT** build a user chat input box. Humans cannot chat with the LLM.
   - Data flow is strictly unidirectional: `Live/Sim Telemetry -> Dual Neural Nets -> Structured Telemetry Payload -> Locked M2M LLM -> Automated Municipal Dispatch & Safe Evacuation Route Output`.
6. **NATIVE OPENSSH ONLY (NO 3RD-PARTY BLOATWARE):**
   - Connect to the remote Windows server (`MSI1`, user `yuvamps1`) strictly via built-in OpenSSH (`ssh` / `scp`). Do not require RustDesk, TeamViewer, or third-party GUI tools.
   - Provide a single native Cloudflare Tunnel command (`cloudflared tunnel --url http://localhost:8000`) for exposing the local `MSI1` backend over HTTPS when remote.

---

## 2. TARGET REPOSITORY STRUCTURE
```text
/home/daksh/Documents/Projects/floodlock/
├── 00_MASTER_GOVERNANCE.md
├── 01_UI_UX_DESIGN_SPEC.md
├── 02_HYDROLOGY_AND_CSV_SPEC.md
├── 03_NEURAL_NET_TRAINING_SPEC.md
├── 04_DUAL_BACKEND_AND_SSH_SPEC.md
├── .env.example
├── data/
│   ├── train_telemetry.csv              # 4,000 rows (Training distribution)
│   └── holdout_unseen_telemetry.csv     # 1,000 rows (Unseen out-of-distribution test set)
├── floodlock_trainer/
│   ├── requirements.txt
│   ├── generate_datasets.py
│   ├── models.py
│   ├── train_models.py
│   ├── run_training.sh
│   ├── run_training.bat
│   ├── checkpoints/
│   └── exports/
│       ├── weights_browser.json         # Synced to floodlock_frontend/data/
│       └── weights_backend.json         # Synced to both backend folders
├── floodlock_backend_local/             # Runs on MSI1 Windows Server (PyTorch + Ollama 162 tok/s)
│   ├── requirements.txt
│   ├── app.py
│   ├── engine/
│   │   ├── harmonizer.py
│   │   ├── neural_infer.py
│   │   ├── router.py
│   │   └── dispatch_slm.py
│   ├── data/
│   │   └── weights_backend.json
│   ├── run_backend.sh
│   └── run_backend.bat
├── floodlock_backend_cloud/             # Cloud Fallback (Render / Railway / Docker ready)
│   ├── Dockerfile
│   ├── render.yaml
│   ├── requirements.txt
│   ├── app.py
│   └── data/
│       └── weights_backend.json
├── floodlock_frontend/                  # 4K Ultra-HD UI (Cloudflare Pages / Netlify ready)
│   ├── netlify.toml
│   ├── index.html
│   ├── css/
│   │   └── dashboard.css
│   ├── js/
│   │   ├── config.js
│   │   ├── inference.js
│   │   ├── map_engine.js
│   │   └── app.js
│   ├── data/
│   │   └── weights_browser.json
│   ├── run_frontend.sh
│   └── run_frontend.bat
└── scripts/
    ├── deploy_to_msi_ssh.sh
    └── start_cloudflare_tunnel.bat
