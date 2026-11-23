#!/usr/bin/env python3
"""
scripts/eval_real_gauges.py
Evaluates numerical hydrology simulator predictions against real historical flood gauge observations.
Loads data/gauge_cases.csv, runs the simulator, and computes Mean Absolute Error (MAE).
"""

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "physics"))

from floodlock_physics_simulator import NumericalHydrologySimulator, LANDMARK_BENCHMARKS


def evaluate_gauges():
    csv_path = PROJECT_ROOT / "data" / "gauge_cases.csv"
    if not csv_path.exists():
        print(f"[FAIL] Missing {csv_path}")
        sys.exit(1)

    sim = NumericalHydrologySimulator()
    errors = []
    rows = []

    print("=" * 82)
    print(f"{'Event':<26} | {'Obs (cm)':<9} | {'Pred (cm)':<10} | {'Err (cm)':<9} | {'Citation'}")
    print("=" * 82)

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            event = r["event"].strip()
            citation = r["source_url_or_citation"].strip()
            is_unverified = "UNVERIFIED" in citation.upper()

            obs_cm = float(r["observed_peak_depth_cm"])

            if event in LANDMARK_BENCHMARKS:
                params = LANDMARK_BENCHMARKS[event]
            else:
                # Default lumped parameter mapping from CSV fields
                params = {
                    "peak_rain_mm_hr": float(r["rain_r0"]),
                    "initial_soil_sat": float(r["soil_sat"]),
                    "ks_mm_hr": 1.5,
                    "psi_mm": 200.0,
                    "impervious": 0.80,
                    "slope": 0.01,
                    "manning_n": 0.02,
                    "tide_surge_m": float(r["tide"]),
                    "outfall_invert_m": 1.5,
                    "flow_length_m": 600.0,
                    "channel_width_m": 35.0,
                    "drain_capacity_mm_hr": 20.0,
                    "lateral_inflow_coeff": 0.3,
                }

            res = sim.simulate_storm_sequence(params)
            pred_cm = res["peak_depth_cm"]
            err_cm = abs(pred_cm - obs_cm)

            if not is_unverified:
                errors.append(err_cm)
                status = f"{err_cm:6.1f} cm"
            else:
                status = "EXCLUDED (UNVERIFIED)"

            print(f"{event:<26} | {obs_cm:9.1f} | {pred_cm:10.1f} | {status:<9} | {citation}")

    print("=" * 82)
    if not errors:
        print("[FAIL] Zero verified cases found to compute MAE.")
        sys.exit(1)

    mae = sum(errors) / len(errors)
    print(f"Verified Gauge Cases Evaluated: {len(errors)}")
    print(f"Mean Absolute Error (MAE): {mae:.2f} cm")
    return mae


if __name__ == "__main__":
    evaluate_gauges()

