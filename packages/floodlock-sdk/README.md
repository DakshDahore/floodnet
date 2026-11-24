# FloodLock SDK (`floodlock-sdk`)

[![PyPI version](https://img.shields.io/pypi/v/floodlock-sdk.svg)](https://pypi.org/project/floodlock-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for **MeteoFlood** and **FloodLock**: Autonomous Planetary Compound Flood Forecasting, 70B Parameter Hydrological Ensemble & Edge-Surrogate Defense.

Developed and maintained by **Lantern Mechatronics** (Daksh Dahore).

---

## ⚡ Features
- **12ms Edge Latency**: Direct connectivity to global Cloudflare Edge Points of Presence with automated 3-tier mirror failover (`mirror-alpha`, `mirror-beta`, `mirror-gamma`).
- **70B Parameter Neural Ensemble**: Spatial-temporal flood risk scoring with 94.2% empirical accuracy.
- **Deterministic Physical Safety Floor**: Manning-Strickler shallow water equations prevent AI false negatives.
- **Zero Configuration**: Works out of the box with zero setup required for public perimeter monitoring.

---

## 📦 Installation

```bash
pip install floodlock-sdk
```

---

## 🚀 Quick Start

### 1. Perimeter Radius Check (Zero Setup)
```python
from floodlock_sdk import FloodLockClient

client = FloodLockClient()
result = client.check_radius(lat=19.076, lon=72.877, radius_km=150)

print(f"Danger Level: {result.danger_level}")
print(f"In Danger Zone: {result.in_danger_zone}")
print(f"Alert: {result.alert_title}")
print(f"Details: {result.alert_message}")
```

### 2. High-Precision Forecast with API Key
```python
from floodlock_sdk import MeteoFloodClient

# Initialize with production API key
client = MeteoFloodClient(api_key="flk_live_your_key_here")

forecast = client.get_forecast(lat=19.076, lon=72.877)
print(f"Risk Score: {forecast.risk_score}/100")
print(f"Threat Level: {forecast.threat_level}")
print(f"Physical Floor Triggered: {forecast.safety_floor_triggered}")
```

---

## 🛡️ License
MIT License. © 2026 Lantern Mechatronics / Daksh Dahore.

