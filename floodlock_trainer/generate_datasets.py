"""
floodlock_trainer/generate_datasets.py
────────────────────────────────────────────────────────────────────────────
Hydrodynamic Physics & Wind-Augmented Synthesizer for Mumbai F-South Ward.
Calibrated for Hindmata Basin (19.0160° N, 72.8430° E) & Love Grove Outfall (19.0065° N, 72.8165° E).

Generates:
  - data/train_telemetry.csv (4,000 rows)
  - data/holdout_unseen_telemetry.csv (1,000 rows)

Exact CSV Headers:
rain_instant_mm_hr,rain_1hr_mm_hr,pressure_hpa,tide_astro_m,wind_speed_ms,wind_dir_deg,subsidence_mm_yr,effective_tide_m,choke_pct,eta_minutes
"""

import os
import csv
import math
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRAIN_CSV = os.path.join(DATA_DIR, "train_telemetry.csv")
HOLDOUT_CSV = os.path.join(DATA_DIR, "holdout_unseen_telemetry.csv")


def compute_hydrology_record(
    rain_instant: float,
    rain_1hr: float,
    pressure: float,
    tide_astro: float,
    wind_speed: float,
    wind_dir: float,
    subsidence: float,
    add_jitter: bool = True,
    rng: np.random.Generator = None
) -> dict:
    """
    Implements the exact physical equations from 02_HYDROLOGY_AND_CSV_SPEC.md.
    """
    if rng is None:
        rng = np.random.default_rng()

    # 1. Onshore wind component towards Worli/Mahim coastline (theta_shore = 250.0 degrees)
    theta_shore = 250.0
    wind_angle_rad = math.radians(wind_dir - theta_shore)
    v_onshore = max(0.0, wind_speed * math.cos(wind_angle_rad))

    # 2. Wind-driven coastal surge (meters)
    delta_h_wind = 0.00048 * (v_onshore ** 2)

    # 3. Wind-driven convective/orographic rain intensity multiplier
    r_eff = rain_instant * (1.0 + 0.006 * v_onshore)

    # 4. Inverted Barometer Surge (meters) (+1 cm per 1 hPa below 1013.25 hPa)
    delta_h_baro = max(0.0, (1013.25 - pressure) * 0.01)

    # 5. Effective Coastal Sea Level at Love Grove Outfall (meters MSL)
    h_eff = tide_astro + delta_h_baro + delta_h_wind

    # 6. BRIMSTOWAD Gravity Drainage Cap & Sluice Choke
    # Invert = 3.00 m MSL, begins choking at 2.60 m MSL
    if h_eff <= 2.60:
        choke_ratio = 0.0
    elif h_eff >= 3.00:
        choke_ratio = 1.0
    else:
        choke_ratio = (h_eff - 2.60) / (3.00 - 2.60)

    q_drain = 25.0 * (1.0 - choke_ratio)
    choke_pct = choke_ratio * 100.0

    # 7. Net Basin Accumulation (Hindmata Saucer)
    q_inflow = 0.70 * r_eff + 0.30 * rain_1hr
    delta_q = max(0.0, q_inflow - q_drain)

    # 8. InSAR Subsidence storage capacity compaction factor
    storage_factor = 1.0 - (subsidence / 110.0)
    basin_threshold_mm = 45.0 * storage_factor

    # 9. Time to Inundation (ETA in minutes)
    if delta_q > 1.0:
        jitter = rng.normal(0.0, 1.2) if add_jitter else 0.0
        eta_raw = (basin_threshold_mm / delta_q) * 60.0 + jitter
        eta_minutes = float(np.clip(eta_raw, 2.0, 180.0))
    else:
        eta_minutes = 180.0

    return {
        "rain_instant_mm_hr": round(rain_instant, 2),
        "rain_1hr_mm_hr": round(rain_1hr, 2),
        "pressure_hpa": round(pressure, 2),
        "tide_astro_m": round(tide_astro, 3),
        "wind_speed_ms": round(wind_speed, 2),
        "wind_dir_deg": round(wind_dir, 1),
        "subsidence_mm_yr": round(subsidence, 2),
        "effective_tide_m": round(h_eff, 4),
        "choke_pct": round(choke_pct, 2),
        "eta_minutes": round(eta_minutes, 2),
    }


def generate_training_dataset(n_samples: int = 4000, seed: int = 42) -> str:
    """
    Generates data/train_telemetry.csv with 4,000 rows spanning regular and severe monsoon regimes.
    """
    rng = np.random.default_rng(seed)
    records = []

    for _ in range(n_samples):
        # Sample environmental parameters across typical Mumbai monsoon profiles
        # 60% standard monsoon showers, 40% intense storm events
        if rng.random() < 0.60:
            rain_instant = float(rng.uniform(0.0, 80.0))
            rain_1hr = float(np.clip(rain_instant * rng.uniform(0.60, 1.10), 0.0, 90.0))
            pressure = float(rng.uniform(995.0, 1016.0))
            tide_astro = float(rng.uniform(1.2, 4.2))
            wind_speed = float(rng.uniform(1.0, 18.0))
            wind_dir = float(rng.uniform(0.0, 360.0))
            subsidence = float(rng.uniform(2.0, 25.0))
        else:
            rain_instant = float(rng.uniform(80.0, 160.0))
            rain_1hr = float(np.clip(rain_instant * rng.uniform(0.70, 1.15), 0.0, 160.0))
            pressure = float(rng.uniform(980.0, 1005.0))
            tide_astro = float(rng.uniform(2.5, 4.7))
            wind_speed = float(rng.uniform(10.0, 28.0))
            # Heavier onshore bias during severe events
            wind_dir = float(rng.normal(250.0, 35.0) % 360.0)
            subsidence = float(rng.uniform(5.0, 32.0))

        rec = compute_hydrology_record(
            rain_instant=rain_instant,
            rain_1hr=rain_1hr,
            pressure=pressure,
            tide_astro=tide_astro,
            wind_speed=wind_speed,
            wind_dir=wind_dir,
            subsidence=subsidence,
            add_jitter=True,
            rng=rng
        )
        records.append(rec)

    os.makedirs(DATA_DIR, exist_ok=True)
    fieldnames = [
        "rain_instant_mm_hr",
        "rain_1hr_mm_hr",
        "pressure_hpa",
        "tide_astro_m",
        "wind_speed_ms",
        "wind_dir_deg",
        "subsidence_mm_yr",
        "effective_tide_m",
        "choke_pct",
        "eta_minutes"
    ]

    with open(TRAIN_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"[✓] Created {TRAIN_CSV} ({len(records)} rows)")
    return TRAIN_CSV


def generate_holdout_dataset(n_samples: int = 1000, seed: int = 999) -> str:
    """
    Generates data/holdout_unseen_telemetry.csv with 1,000 rows.
    Spans out-of-distribution extremes, compound disasters (July 2005/2023 tails),
    and edge cases for strict generalization evaluation.
    """
    rng = np.random.default_rng(seed)
    records = []

    for i in range(n_samples):
        # 5 distinct out-of-distribution regimes
        regime = i % 5

        if regime == 0:
            # Extreme Cloudburst with moderate tide (July 2005 disaster tail)
            rain_instant = float(rng.uniform(140.0, 195.0))
            rain_1hr = float(rng.uniform(120.0, 180.0))
            pressure = float(rng.uniform(960.0, 985.0))
            tide_astro = float(rng.uniform(3.5, 4.8))
            wind_speed = float(rng.uniform(22.0, 35.0))
            wind_dir = float(rng.uniform(240.0, 260.0))
            subsidence = float(rng.uniform(14.0, 35.0))

        elif regime == 1:
            # Sunny-day King Tide / Storm Surge Backflow (Tide >= 4.8m MSL, Zero rain)
            rain_instant = float(rng.uniform(0.0, 5.0))
            rain_1hr = float(rng.uniform(0.0, 5.0))
            pressure = float(rng.uniform(970.0, 1000.0))
            tide_astro = float(rng.uniform(4.5, 5.2))
            wind_speed = float(rng.uniform(18.0, 32.0))
            wind_dir = float(rng.uniform(230.0, 270.0))
            subsidence = float(rng.uniform(10.0, 30.0))

        elif regime == 2:
            # Offshore Gale (Wind 30 m/s at 70° - no surge, low tide, but sudden downpour)
            rain_instant = float(rng.uniform(90.0, 160.0))
            rain_1hr = float(rng.uniform(70.0, 140.0))
            pressure = float(rng.uniform(985.0, 1010.0))
            tide_astro = float(rng.uniform(1.0, 2.2))
            wind_speed = float(rng.uniform(15.0, 32.0))
            wind_dir = float(rng.uniform(60.0, 90.0))  # Offshore
            subsidence = float(rng.uniform(0.8, 15.0))

        elif regime == 3:
            # High Subsidence Compaction Basin (Hindmata worst-case soil compression)
            rain_instant = float(rng.uniform(60.0, 130.0))
            rain_1hr = float(rng.uniform(50.0, 110.0))
            pressure = float(rng.uniform(980.0, 1008.0))
            tide_astro = float(rng.uniform(3.0, 4.4))
            wind_speed = float(rng.uniform(12.0, 24.0))
            wind_dir = float(rng.uniform(180.0, 300.0))
            subsidence = float(rng.uniform(28.0, 35.0))  # Extreme subsidence

        else:
            # Sub-nominal benign lull / recovery conditions
            rain_instant = float(rng.uniform(0.0, 15.0))
            rain_1hr = float(rng.uniform(0.0, 10.0))
            pressure = float(rng.uniform(1010.0, 1022.0))
            tide_astro = float(rng.uniform(1.0, 2.4))
            wind_speed = float(rng.uniform(0.0, 8.0))
            wind_dir = float(rng.uniform(0.0, 360.0))
            subsidence = float(rng.uniform(0.8, 14.2))

        rec = compute_hydrology_record(
            rain_instant=rain_instant,
            rain_1hr=rain_1hr,
            pressure=pressure,
            tide_astro=tide_astro,
            wind_speed=wind_speed,
            wind_dir=wind_dir,
            subsidence=subsidence,
            add_jitter=True,
            rng=rng
        )
        records.append(rec)

    os.makedirs(DATA_DIR, exist_ok=True)
    fieldnames = [
        "rain_instant_mm_hr",
        "rain_1hr_mm_hr",
        "pressure_hpa",
        "tide_astro_m",
        "wind_speed_ms",
        "wind_dir_deg",
        "subsidence_mm_yr",
        "effective_tide_m",
        "choke_pct",
        "eta_minutes"
    ]

    with open(HOLDOUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"[✓] Created {HOLDOUT_CSV} ({len(records)} rows)")
    return HOLDOUT_CSV


def generate_all():
    print("==================================================================")
    print(" PROJECT FLOODLOCK // HYDRODYNAMIC SYNTHESIZER & CSV PIPELINE")
    print("==================================================================")
    train_path = generate_training_dataset(4000, seed=42)
    holdout_path = generate_holdout_dataset(1000, seed=999)
    print("==================================================================")
    print(f" [✓] Datasets generated successfully in {DATA_DIR}")
    print("==================================================================")
    return train_path, holdout_path


if __name__ == "__main__":
    generate_all()
