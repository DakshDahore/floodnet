"""
floodlock_backend_local/engine/harmonizer.py
────────────────────────────────────────────────────────────────────────────
Hydrodynamic Physics Harmonizer for Mumbai F-South Ward.
Computes:
  - Onshore wind vectoring (250° azimuth Worli/Mahim Bay)
  - Coastal wind setup & inverted barometer surge
  - BRIMSTOWAD 25.0 mm/hr sluice choke (2.60m to 3.00m MSL at Love Grove)
  - InSAR vertical subsidence storage compaction
  - Net accumulation & physical time-to-inundation (ETA)
"""

import math


def calculate_hydrodynamic_state(
    rain_instant: float,
    rain_1hr: float,
    pressure: float,
    tide_astro: float,
    wind_speed: float,
    wind_dir: float,
    subsidence: float = 14.2,
    antecedent_depth_m: float = 0.0
) -> dict:
    """
    Evaluates exact physics calibration for Hindmata Saucer & Love Grove Outfall.
    antecedent_depth_m: Standing water depth (in meters) already present from previous rainfall.
    """
    # 1. Onshore wind vector towards Worli/Mahim coastline (theta_shore = 250.0 degrees)
    theta_shore = 250.0
    wind_angle_rad = math.radians(wind_dir - theta_shore)
    v_onshore = max(0.0, wind_speed * math.cos(wind_angle_rad))

    # 2. Coastal wind surge (meters)
    delta_h_wind = 0.00048 * (v_onshore ** 2)

    # 3. Orographic / convective rain amplification
    r_eff = rain_instant * (1.0 + 0.006 * v_onshore)
    rain_amplification_pct = max(0.0, ((r_eff - rain_instant) / (rain_instant + 1e-6)) * 100.0)

    # 4. Inverted Barometer Surge (meters) (+1 cm per 1 hPa below 1013.25 hPa)
    delta_h_baro = max(0.0, (1013.25 - pressure) * 0.01)

    # 5. Effective Coastal Sea Level at Love Grove Outfall
    effective_tide_m = tide_astro + delta_h_baro + delta_h_wind

    # 6. BRIMSTOWAD Gravity Drainage Choke (Invert: 3.00m MSL, starts choking at 2.60m MSL)
    if effective_tide_m <= 2.60:
        choke_ratio = 0.0
    elif effective_tide_m >= 3.00:
        choke_ratio = 1.0
    else:
        choke_ratio = (effective_tide_m - 2.60) / (3.00 - 2.60)

    choke_pct = choke_ratio * 100.0
    q_drain = 25.0 * (1.0 - choke_ratio)

    # 7. Net Basin Accumulation (Hindmata Saucer)
    q_inflow = 0.70 * r_eff + 0.30 * rain_1hr
    delta_q = max(0.0, q_inflow - q_drain)

    # 8. InSAR Storage Compaction Factor & Antecedent Capacity Reduction
    storage_factor = 1.0 - (subsidence / 110.0)
    nominal_threshold_mm = 45.0 * storage_factor

    # Antecedent standing water reduces remaining retention volume
    capacity_remaining_ratio = max(0.10, 1.0 - (antecedent_depth_m / 0.45))
    basin_threshold_mm = nominal_threshold_mm * capacity_remaining_ratio

    # 9. Time to Inundation (ETA in minutes)
    if delta_q > 1.0:
        eta_physics = (basin_threshold_mm / delta_q) * 60.0
        eta_physics = max(2.0, min(180.0, eta_physics))
    else:
        eta_physics = 180.0 if antecedent_depth_m < 0.15 else max(15.0, 180.0 - (antecedent_depth_m * 200.0))

    # 10. Total street water depth = Antecedent Standing Depth + New Accumulation
    new_ponding_depth = (delta_q / 50.0) * 0.35 if delta_q > 1.0 else 0.0
    total_water_depth_m = max(0.0, antecedent_depth_m + new_ponding_depth)
    total_water_depth_m = round(min(1.85, total_water_depth_m), 2)

    return {
        "inputs": {
            "rain_instant_mm_hr": round(rain_instant, 2),
            "rain_1hr_mm_hr": round(rain_1hr, 2),
            "pressure_hpa": round(pressure, 2),
            "tide_astro_m": round(tide_astro, 3),
            "wind_speed_ms": round(wind_speed, 2),
            "wind_dir_deg": round(wind_dir, 1),
            "subsidence_mm_yr": round(subsidence, 2)
        },
        "wind_physics": {
            "v_onshore_ms": round(v_onshore, 2),
            "wind_surge_m": round(delta_h_wind, 4),
            "baro_surge_m": round(delta_h_baro, 4),
            "rain_amplification_pct": round(rain_amplification_pct, 1),
            "effective_rain_mm_hr": round(r_eff, 2)
        },
        "hydrology": {
            "effective_tide_m": round(effective_tide_m, 3),
            "sluice_choke_pct": round(choke_pct, 1),
            "q_drain_mm_hr": round(q_drain, 2),
            "q_inflow_mm_hr": round(q_inflow, 2),
            "net_accumulation_mm_hr": round(delta_q, 2),
            "basin_threshold_mm": round(basin_threshold_mm, 2),
            "water_depth_m": total_water_depth_m,
            "eta_physics_minutes": round(eta_physics, 1),
            "is_hydraulic_locked": choke_pct >= 99.0
        }
    }
