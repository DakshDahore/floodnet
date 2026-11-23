# FloodLock Hydrological Neural Surrogate & Model Training Pipeline

## Overview
This directory contains the training and calibration pipeline for the 14-feature edge neural surrogate network deployed across FloodLock Cloudflare Workers.

## Model Architecture & Scope
- **Classification**: Zero-Dimensional Lumped Kinematic Storage Model surrogate.
- **Input Features (14)**:
  `["r0_norm", "r48_norm", "r120_norm", "cape_norm", "dp_norm", "wind_norm", "spi30_norm", "spi90_norm", "soil_sat", "ks_norm", "water_prox", "twi", "impervious", "tide_surge_norm"]`
- **Layers**:
  - Layer 1: Dense $(14 \to 32)$, ReLU activation
  - Layer 2: Dense $(32 \to 16)$, ReLU activation
  - Layer 3: Multi-Head Output:
    - Head 1: `depth_trajectory_cm` (+1h, +3h, +6h forecast)
    - Head 2: `runoff_q_m3s` (peak catchment discharge)
    - Head 3: `flash_flood_probability` (sigmoid logit)
    - Head 4: `urgency_score` (civic priority index)

## Verification Metrics & Honest Performance Evaluation

| Evaluation Regime | Metric | Value | Description |
| :--- | :--- | :--- | :--- |
| **Synthetic Simulator Holdout (`X_val`)** | Depth MAE | **3.96 cm** | Surrogate emulation error against the 0D lumped physics simulator across 15,000 synthetic holdout sequences. |
| **Synthetic Simulator Holdout (`X_val`)** | Runoff MAE | **9.50 m³/s** | Peak volumetric discharge emulation accuracy against lumped simulator. |
| **Synthetic Simulator Holdout (`X_val`)** | Flood Probability MAE | **0.0102** | Binary classification calibration on inundation boundaries. |
| **Real Historical Gauge Observations** | Mean Absolute Error | **~75 cm** | Evaluated against 6 real-world historical gauge records (Mumbai 2005/2021, Valencia 2024, Zhengzhou 2021, Houston USGS, Sahara). |

### Why Real Gauge Observations Diverge from 0D Lumped Models
A zero-dimensional lumped kinematic storage model computes mass conservation over an idealized catchment box coupling Green-Ampt infiltration with Manning discharge. In complex real-world terrain (such as the Valencia Paiporta canyon torrent or Zhengzhou subway breach), 2D momentum funneling, channel geomorphology, and urban infrastructure bottlenecks concentrate runoff into extreme local flood crests (e.g. 225 cm observed vs 22 cm lumped).

**This physical divergence is the exact raison d’être of FloodLock's multi-layered defense:**
1. The **Deterministic Physical Hazard Floor** does NOT rely on the surrogate's depth prediction alone. It triggers on raw rainfall rate ($R_0 \ge 15\text{ mm/hr}$), antecedent rain ($R_{48} \ge 50\text{ mm}$), or coastal surge ($\ge 1.5\text{m}$), forcing emergency alerts regardless of neural depth under-prediction.
2. The **Adversarial Groq Reasoning Gate** verifies physical plausibility against live hydrometeorological telemetry.
3. The neural surrogate serves strictly as an ultra-fast (<0.2ms) early-warning triaging filter across millions of planetary quadtree cells.

## 10 Historical Landmark Benchmarks
The lumped simulator (`floodlock_physics_simulator.py`) enforces strict mass conservation ($\Delta h = P - I - Q$) across 10 benchmark storm profiles:
1. `sahara_control` (Zero rain, dry baseline, strictly 0.0 cm depth)
2. `mumbai_2005_deluge` (185 mm/hr peak, 4.48m spring tide lock)
3. `dubai_2024_cloudburst` (110 mm/hr peak, clay crust, 95% impervious)
4. `valencia_2024_barranco` (165 mm/hr peak, steep ravine flash discharge)
5. `zhengzhou_2021_megacity` (201.9 mm/hr peak, 98% impervious urban seal)
6. `hurricane_ida_nyc_2021` (80 mm/hr peak, dense subway & basement inundation)
7. `ahr_valley_2021_fluvial` (145 mm/hr peak, mountain gorge runoff funnel)
8. `pakistan_2022_monsoon` (95 mm/hr peak, basin water entrapment)
9. `jeddah_2022_flash` (182 mm/hr peak, arid alluvial wadi breach)
10. `brisbane_2022_tidal` (120 mm/hr peak, coastal riverback surge lock)

## Running Verification
```bash
# Verify mass conservation offline across all 10 benchmarks
python3 test_physics_conservation.py

# Run master zero-network audit suite
python3 scripts/verify_offline_audit_suite.py
```
