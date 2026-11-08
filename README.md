# 🌊 FloodNet / FloodLock — Urban Flood Intelligence & Neural Backflow Engine

[![Live Web Application](https://img.shields.io/badge/Live_App-floodnet.netlify.app-00C7B7?style=for-the-badge&logo=netlify)](https://floodnet.netlify.app)
[![Cloudflare Edge Backend](https://img.shields.io/badge/Edge_Backend-Cloudflare_Workers-F38020?style=for-the-badge&logo=cloudflare)](https://floodlock-backend.dakshdahore1995.workers.dev)
[![Target Precinct](https://img.shields.io/badge/Target_Precinct-Mumbai_F--South_Ward-3B82F6?style=for-the-badge)](https://floodnet.netlify.app)

**FloodNet (FloodLock)** is a 3-tier real-time urban flood prediction, hydraulic backflow analysis, and disaster early-warning system developed for high-density flood-vulnerable coastal basins (centered on Mumbai F-South Ward: Hindmata Basin & Love Grove Outfall).

---

## ⚡ Live Deployments

- **Web Dashboard:** [https://floodnet.netlify.app](https://floodnet.netlify.app)
- **Cloudflare 24/7 Edge Backend:** [https://floodlock-backend.dakshdahore1995.workers.dev](https://floodlock-backend.dakshdahore1995.workers.dev)

---

## 🏗 System Architecture

```
                  ┌───────────────────────────────────────────────┐
                  │             LIVE METEOROLOGY & TIDE          │
                  │   Open-Meteo REST • Storm Tide • Subsidence   │
                  └──────────────────────┬────────────────────────┘
                                         │
                                         ▼
                  ┌───────────────────────────────────────────────┐
                  │        DUAL NEURAL NETWORK ENGINE (MLP)       │
                  │   Tier-1: Browser Edge MLP (209 Parameters)   │
                  │   Tier-2: Deep Hydraulic PyTorch Server MLP   │
                  └──────────────────────┬────────────────────────┘
                                         │
                                         ▼
                  ┌───────────────────────────────────────────────┐
                  │        TACTICAL CRISIS COMMAND DECK           │
                  │   4K Tactical 3D Geospatial Map (Cesium/OSM)  │
                  │   Hindmata Retention Tank Inundation Simulator│
                  │   Love Grove Hydraulic Backflow Warning Gates │
                  └──────────────────────┬────────────────────────┘
                                         │
                                         ▼
                  ┌───────────────────────────────────────────────┐
                  │        M2M DISPATCH & EVACUATION ADVISORY     │
                  │   Autonomous Municipal Alert Routing Engine   │
                  └───────────────────────────────────────────────┘
```

---

## 🧠 Dual Neural Network Topology

### Tier-1: Browser Edge Network (`BrowserEdgeMLP` — 209 Parameters)
- Evaluates at `<0.05 ms` directly inside client JavaScript at 60 FPS slider updates.
- **Inputs:** Normalized Instant Rain, Effective Tide, Subsidence.
- **Architecture:** `Linear(3, 16) -> ReLU -> Linear(16, 8) -> ReLU -> Linear(8, 1)` $\implies \mathbf{209}$ trainable parameters.

### Tier-2: Deep Hydrology Server Network
- Deep PyTorch model modeling rainfall-runoff delay, retention tank capacity saturation, and gravitational sluice gate backflow risks.

---

## 🕹 Simulation & Replay Scenarios

1. **Live Mumbai Telemetry:** Streams real-time precipitation, wind vector, barometric pressure, and astronomical tide.
2. **July 2023 Cloudburst:** High-intensity monsoon historical replay.
3. **July 2005 Catastrophe:** Historical crisis simulation (944 mm 24-hr record event).
4. **Manual Stress Simulator:** Real-time 60 FPS slider controls for water levels, rainfall, and sea surge.

---

## 🛠 Local Setup & Running

```bash
# Clone the repository
git clone https://github.com/DakshDahore/floodnet.git
cd floodnet

# Launch frontend locally
cd floodlock_frontend
python3 -m http.server 3000
```
Open `http://localhost:3000` in your web browser.

---

## 👥 Authors
- **Daksh Dahore** ([@DakshDahore](https://github.com/DakshDahore))
- Built for Hack Club & Urban Disaster Resilience Research.

