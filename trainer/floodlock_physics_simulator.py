"""
physics/floodlock_physics_simulator.py
================================================================================
FloodLock v3.0 — ENGINE 1: Mass-Conserving First-Principles Hydrology Simulator
================================================================================
Hardened Remedies Implemented:
  1. Strict SI Unit Consistency: All fluxes solved in meters (m) and seconds (s)
     over explicit catchment geometry (flow_length_m, cell_width_m).
  2. Supply-Limited Green-Ampt Infiltration:
     - Tracks cumulative soil infiltration F_soil(t) strictly on the pervious
       fraction (preventing impervious dilution of wetting-front depth).
     - Regularized initial wetting front F_eff >= 2 mm (eliminates 1/0 singularity).
     - Draws infiltration from BOTH rainfall AND ponded surface depth (R + h/dt),
       guaranteeing h >= 0 and realistic post-storm drainage.
  3. CFL-Substepped Manning Kinematic Wave + Municipal Outfall Capacity:
     - Subdivides each macroscopic timestep (dt_sec = 600s) into 12 substeps
       (50s each) and caps outflow by available mobile depth (h - depression),
       eliminating explicit Euler overshoot and negative water depths.
     - Models finite urban storm-sewer outfall capacity (e.g., Mumbai BRIMSTOWAD
       25 mm/hr, Dubai 5 mm/hr, Zhengzhou 35 mm/hr) alongside overland sheet flow.
  4. Clamped Tidal Outfall Choke + Head-Driven Orifice Backwater:
     - Outflow choke factor strictly bounded in [0.10, 1.00] (never negative,
       eliminating mass-creation blow-up at Mumbai 4.48m spring tide).
     - Seawater backwater intrusion governed by physical head difference
       delta_H = max(0, H_tide - (Z_invert + h)) via submerged orifice flow,
       naturally reaching hydrostatic equilibrium instead of pumping infinitely.
  5. Exact 6-Hour Physical Horizon:
     - Simulates 36 timesteps x 600s = 6.0 hours (reporting true +1h, +3h, +6h
       inundation depths instead of 10m/30m/60m).
  6. Continuous Mass-Balance Residual Verification:
     - Tracks cumulative inflow, infiltration, outflow, backwater, and stored
       depth; asserts |mass_residual_m| < 1e-9 m at every timestep.
"""

from __future__ import annotations

import csv
import math
from typing import Dict, List, Optional, Tuple

import numpy as np


class NumericalHydrologySimulator:
    """Mass-conserving numerical hydrology solver for FloodLock Engine 1."""

    def __init__(self, gravity: float = 9.81, substeps: int = 12):
        self.g = gravity
        self.substeps = max(4, int(substeps))

    @staticmethod
    def _validate_state(state: Dict[str, float]) -> None:
        if state["rain_rate_mm_hr"] < 0.0:
            raise ValueError("rain_rate_mm_hr must be non-negative")
        if not (0.0 <= state["impervious"] <= 1.0):
            raise ValueError("impervious fraction must be in [0, 1]")
        if not (0.0 <= state["soil_sat"] <= 1.0):
            raise ValueError("soil_sat must be in [0, 1]")
        if state["manning_n"] <= 0.0:
            raise ValueError("manning_n must be strictly positive")
        if state["ks_mm_hr"] < 0.0:
            raise ValueError("ks_mm_hr must be non-negative")
        if state["slope"] < 0.0:
            raise ValueError("slope must be non-negative")

    def solve_timestep(self, state: Dict[str, float], dt_sec: float = 600.0) -> Dict[str, float]:
        """
        Solves one macroscopic timestep dt_sec using adaptive sub-stepping.
        Strictly enforces:
            h_{t+dt} - h_t = Inflow_step - Infil_step - Outflow_step + Backwater_step
            h >= 0.0 always.
        """
        self._validate_state(state)

        rain_rate_m_s = (state["rain_rate_mm_hr"] / 1000.0) / 3600.0
        lateral_inflow_m_s = (state.get("lateral_inflow_mm_hr", 0.0) / 1000.0) / 3600.0
        soil_sat = state["soil_sat"]
        ks_m_s = (state["ks_mm_hr"] / 1000.0) / 3600.0
        psi_m = max(0.0, state["psi_mm"] / 1000.0)
        impervious = state["impervious"]
        pervious = max(0.0, 1.0 - impervious)
        slope = max(1e-5, state["slope"])
        manning_n = state["manning_n"]
        tide_surge_m = state["tide_surge_m"]
        outfall_invert_m = state["outfall_invert_m"]

        # Catchment geometry & municipal drainage capacity
        flow_length_m = max(30.0, float(state.get("flow_length_m", 350.0)))
        channel_width_m = max(10.0, float(state.get("channel_width_m", 30.0)))
        drain_cap_mm_hr = state.get("drain_capacity_mm_hr", None)
        drain_cap_m_s = (
            (float(drain_cap_mm_hr) / 1000.0) / 3600.0
            if drain_cap_mm_hr is not None
            else None
        )
        porosity = float(state.get("porosity", 0.45))
        depression_m = float(state.get("depression_storage_m", 0.005))
        orifice_k = float(state.get("backwater_orifice_coeff", 1.5e-5))

        h = max(0.0, float(state.get("depth_m", 0.0)))
        h_initial = h
        F_soil_m = max(0.0, float(state.get("cum_infil_mm", 0.0)) / 1000.0)
        delta_theta = max(0.02, porosity * (1.0 - soil_sat))

        # Tidal outfall choke ratio strictly clamped to [0, 1]
        if tide_surge_m > outfall_invert_m:
            choke_ratio = min(1.0, max(0.0, (tide_surge_m - outfall_invert_m) / 1.5))
            drain_efficiency = max(0.10, 1.0 - 0.90 * choke_ratio)
        else:
            choke_ratio = 0.0
            drain_efficiency = 1.0

        sub_dt = dt_sec / self.substeps
        total_inflow_m = 0.0
        total_infil_m = 0.0
        total_outflow_m = 0.0
        total_backwater_m = 0.0
        peak_q_m3_s = 0.0

        for _ in range(self.substeps):
            # 1. Precipitation + upstream lateral inflow
            inflow_m = (rain_rate_m_s + lateral_inflow_m_s) * sub_dt
            total_inflow_m += inflow_m
            available_m = h + inflow_m

            # 2. Supply-limited Green-Ampt infiltration on pervious fraction
            if pervious > 0.0 and ks_m_s > 0.0 and available_m > 0.0:
                F_eff_m = max(F_soil_m, 0.002)
                f_pot_soil_m_s = ks_m_s * (1.0 + (psi_m * delta_theta) / F_eff_m)
                max_infil_basin_m = f_pot_soil_m_s * pervious * sub_dt
                infil_basin_m = min(available_m, max_infil_basin_m)
                F_soil_m += infil_basin_m / pervious
            else:
                infil_basin_m = 0.0

            total_infil_m += infil_basin_m
            h_after_infil = max(0.0, available_m - infil_basin_m)

            # 3. Head-driven submerged orifice tidal backwater intrusion
            water_surface_elev_m = outfall_invert_m + h_after_infil
            if tide_surge_m > water_surface_elev_m and choke_ratio > 0.0:
                net_head_m = tide_surge_m - water_surface_elev_m
                v_orifice_m_s = math.sqrt(2.0 * self.g * net_head_m)
                q_backwater_m_s = orifice_k * choke_ratio * v_orifice_m_s
                backwater_m = min(net_head_m, q_backwater_m_s * sub_dt)
            else:
                backwater_m = 0.0

            total_backwater_m += backwater_m
            h_before_drain = h_after_infil + backwater_m

            # 4. Manning kinematic sheet/channel flow + municipal outfall cap
            h_mobile = max(0.0, h_before_drain - depression_m)
            if h_mobile > 0.0:
                v_overland_m_s = (1.0 / manning_n) * (h_mobile ** (2.0 / 3.0)) * math.sqrt(slope)
                q_unit_m2_s = v_overland_m_s * h_mobile  # Discharge per meter width [m^2/s]
                outflow_rate_m_s = (q_unit_m2_s / flow_length_m) * drain_efficiency

                # Urban sink / municipal storm-drain throttle (if applicable)
                if drain_cap_m_s is not None:
                    outflow_rate_m_s = min(outflow_rate_m_s, drain_cap_m_s * drain_efficiency)

                q_channel_m3_s = q_unit_m2_s * channel_width_m * drain_efficiency
                peak_q_m3_s = max(peak_q_m3_s, q_channel_m3_s)

                outflow_m = min(h_mobile, outflow_rate_m_s * sub_dt)
            else:
                outflow_m = 0.0

            total_outflow_m += outflow_m
            h = max(0.0, h_before_drain - outflow_m)

        # 5. Machine-Precision Mass Conservation Audit
        expected_h = h_initial + total_inflow_m - total_infil_m - total_outflow_m + total_backwater_m
        mass_residual_m = abs(h - expected_h)
        if mass_residual_m > 1e-9:
            raise RuntimeError(f"Mass conservation violated: residual={mass_residual_m:.3e} m")

        reported_depth_cm = max(0.0, (h - depression_m) * 100.0)
        avg_infil_mm_hr = (total_infil_m * 1000.0) / (dt_sec / 3600.0)
        avg_backwater_mm_hr = (total_backwater_m * 1000.0) / (dt_sec / 3600.0)

        return {
            "depth_m": h,
            "depth_cm": round(reported_depth_cm, 2),
            "cum_infil_mm": round(F_soil_m * 1000.0, 4),
            "runoff_q_m3s": round(peak_q_m3_s, 3),
            "infil_rate_mm_hr": round(avg_infil_mm_hr, 2),
            "backwater_rate_mm_hr": round(avg_backwater_mm_hr, 2),
            "choke_ratio": round(choke_ratio, 4),
            "mass_residual_m": mass_residual_m,
            "inflow_step_m": total_inflow_m,
            "infil_step_m": total_infil_m,
            "outflow_step_m": total_outflow_m,
            "backwater_step_m": total_backwater_m,
        }

    def simulate_storm_sequence(
        self,
        params: Dict[str, float],
        horizon_hours: int = 6,
        dt_sec: float = 600.0,
    ) -> Dict[str, object]:
        """
        Simulates a full 6-hour storm (36 timesteps x 600s = 21,600s).
        Returns exact +1h, +3h, and +6h depths, peak overland discharge Q,
        flash-flood probability, urgency, and cumulative mass-balance audit.
        """
        steps_per_hour = int(round(3600.0 / dt_sec))
        total_steps = horizon_hours * steps_per_hour

        state = {
            "rain_rate_mm_hr": 0.0,
            "lateral_inflow_mm_hr": 0.0,
            "cum_rain_mm": 0.0,
            "soil_sat": params["initial_soil_sat"],
            "ks_mm_hr": params["ks_mm_hr"],
            "psi_mm": params["psi_mm"],
            "impervious": params["impervious"],
            "slope": params["slope"],
            "manning_n": params["manning_n"],
            "tide_surge_m": params["tide_surge_m"],
            "outfall_invert_m": params["outfall_invert_m"],
            "flow_length_m": params.get("flow_length_m", 350.0),
            "channel_width_m": params.get("channel_width_m", 30.0),
            "drain_capacity_mm_hr": params.get("drain_capacity_mm_hr", None),
            "depth_m": 0.0,
            "cum_infil_mm": 0.0,
        }

        peak_r = max(0.0, float(params["peak_rain_mm_hr"]))
        lateral_mult = max(0.0, float(params.get("lateral_inflow_coeff", 0.0)))

        depth_history_cm: List[float] = []
        runoff_history_q: List[float] = []
        hourly_rain_profile: List[float] = []

        cum_inflow_m = 0.0
        cum_infil_m = 0.0
        cum_outflow_m = 0.0
        cum_backwater_m = 0.0
        max_step_residual_m = 0.0

        for step in range(total_steps):
            phase = ((step + 0.5) / total_steps) * math.pi
            step_rain = peak_r * math.sin(phase)
            state["rain_rate_mm_hr"] = step_rain
            state["lateral_inflow_mm_hr"] = step_rain * lateral_mult
            state["cum_rain_mm"] += step_rain * (dt_sec / 3600.0)

            res = self.solve_timestep(state, dt_sec=dt_sec)
            state["depth_m"] = res["depth_m"]
            state["cum_infil_mm"] = res["cum_infil_mm"]

            depth_history_cm.append(res["depth_cm"])
            runoff_history_q.append(res["runoff_q_m3s"])

            cum_inflow_m += res["inflow_step_m"]
            cum_infil_m += res["infil_step_m"]
            cum_outflow_m += res["outflow_step_m"]
            cum_backwater_m += res["backwater_step_m"]
            max_step_residual_m = max(max_step_residual_m, res["mass_residual_m"])

            if (step + 1) % steps_per_hour == 0:
                hourly_rain_profile.append(round(step_rain, 3))

        idx_1h = min(steps_per_hour - 1, len(depth_history_cm) - 1)
        idx_3h = min(3 * steps_per_hour - 1, len(depth_history_cm) - 1)
        idx_6h = len(depth_history_cm) - 1

        h1 = depth_history_cm[idx_1h]
        h3 = depth_history_cm[idx_3h]
        h6 = depth_history_cm[idx_6h]
        peak_h = max(depth_history_cm) if depth_history_cm else 0.0
        peak_q = max(runoff_history_q) if runoff_history_q else 0.0

        global_expected_h = cum_inflow_m - cum_infil_m - cum_outflow_m + cum_backwater_m
        global_mass_residual_m = abs(state["depth_m"] - global_expected_h)

        assert state["depth_m"] >= 0.0, "Negative water depth detected!"
        assert state["depth_m"] <= (cum_inflow_m + cum_backwater_m + 1e-9), (
            "Depth exceeded total physical inflow (mass creation detected)!"
        )
        assert global_mass_residual_m < 1e-8, (
            f"Global mass residual exceeded tolerance: {global_mass_residual_m:.3e} m"
        )

        if peak_h > 30.0 or peak_q > 15.0 or (h1 > 15.0 and peak_q > 5.0):
            prob = min(1.0, 0.70 + (peak_h / 200.0) + (peak_q / 50.0))
            urgency = min(1.0, 0.65 + (h1 / 150.0) + (peak_q / 40.0))
        elif peak_h > 5.0 or peak_q > 2.0:
            prob = min(0.65, 0.20 + (peak_h / 80.0))
            urgency = min(0.60, 0.15 + (peak_h / 90.0))
        else:
            prob = 0.0
            urgency = 0.0

        return {
            "depth_trajectory": [h1, h3, h6],
            "peak_depth_cm": peak_h,
            "runoff_q": round(peak_q, 3),
            "flood_prob": round(prob, 3),
            "urgency": round(urgency, 3),
            "hourly_rain_mm_hr": hourly_rain_profile,
            "mass_audit": {
                "cum_inflow_m": round(cum_inflow_m, 6),
                "cum_infil_m": round(cum_infil_m, 6),
                "cum_outflow_m": round(cum_outflow_m, 6),
                "cum_backwater_m": round(cum_backwater_m, 6),
                "final_depth_m": round(state["depth_m"], 6),
                "global_mass_residual_m": global_mass_residual_m,
                "max_step_residual_m": max_step_residual_m,
            },
        }


LANDMARK_BENCHMARKS: Dict[str, Dict[str, float]] = {
    "sahara_control": {
        "peak_rain_mm_hr": 0.0, "initial_soil_sat": 0.10, "ks_mm_hr": 35.0,
        "psi_mm": 110.0, "impervious": 0.05, "slope": 0.02, "manning_n": 0.04,
        "tide_surge_m": 0.0, "outfall_invert_m": 2.0,
        "flow_length_m": 100.0, "channel_width_m": 30.0, "drain_capacity_mm_hr": None,
        "lateral_inflow_coeff": 0.0,
    },
    "mumbai_2005_deluge": {
        "peak_rain_mm_hr": 185.0, "initial_soil_sat": 0.96, "ks_mm_hr": 1.2,
        "psi_mm": 250.0, "impervious": 0.88, "slope": 0.002, "manning_n": 0.018,
        "tide_surge_m": 4.48, "outfall_invert_m": 2.0,
        "flow_length_m": 500.0, "channel_width_m": 40.0, "drain_capacity_mm_hr": 25.0,
        "lateral_inflow_coeff": 0.25,
    },
    "dubai_2024_cloudburst": {
        "peak_rain_mm_hr": 110.0, "initial_soil_sat": 0.25, "ks_mm_hr": 0.4,
        "psi_mm": 350.0, "impervious": 0.95, "slope": 0.001, "manning_n": 0.015,
        "tide_surge_m": 0.6, "outfall_invert_m": 1.5,
        "flow_length_m": 800.0, "channel_width_m": 30.0, "drain_capacity_mm_hr": 5.0,
        "lateral_inflow_coeff": 0.15,
    },
    "valencia_2024_barranco": {
        "peak_rain_mm_hr": 165.0, "initial_soil_sat": 0.85, "ks_mm_hr": 4.0,
        "psi_mm": 150.0, "impervious": 0.55, "slope": 0.08, "manning_n": 0.032,
        "tide_surge_m": 0.4, "outfall_invert_m": 2.5,
        "flow_length_m": 1200.0, "channel_width_m": 35.0, "drain_capacity_mm_hr": None,
        "lateral_inflow_coeff": 16.5,  # Steep upstream watershed funneling into barranco gorge
    },
    "zhengzhou_2021_megacity": {
        "peak_rain_mm_hr": 201.9, "initial_soil_sat": 0.90, "ks_mm_hr": 0.05,
        "psi_mm": 100.0, "impervious": 0.98, "slope": 0.004, "manning_n": 0.012,
        "tide_surge_m": 0.0, "outfall_invert_m": 2.0,
        "flow_length_m": 600.0, "channel_width_m": 30.0, "drain_capacity_mm_hr": 35.0,
        "lateral_inflow_coeff": 0.25,
    },
}


def generate_verified_physical_dataset(
    n_samples: int = 10000,
    output_csv: Optional[str] = None,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Generates physically consistent training sequences where the temporal feature
    tensor X[i, 0..5] strictly matches the simulated 6-hour storm hyetograph.
    """
    sim = NumericalHydrologySimulator()
    rng = np.random.default_rng(seed)

    X = np.zeros((n_samples, 6, 14), dtype=np.float32)
    Y_depth = np.zeros((n_samples, 3), dtype=np.float32)
    Y_runoff = np.zeros((n_samples, 1), dtype=np.float32)
    Y_prob = np.zeros((n_samples, 1), dtype=np.float32)
    Y_urgency = np.zeros((n_samples, 1), dtype=np.float32)

    for i in range(n_samples):
        archetype = int(rng.choice([0, 1, 2, 3, 4], p=[0.20, 0.30, 0.25, 0.15, 0.10]))

        if archetype == 0:
            peak_r = float(rng.uniform(0.0, 1.5))
            r48, r120 = peak_r * 2.0, peak_r * 4.0
            cape, dp, wind = float(rng.uniform(100.0, 500.0)), 0.0, 10.0
            spi30, spi90 = -0.5, -0.5
            soil_sat = float(rng.uniform(0.1, 0.4))
            ks, psi = float(rng.uniform(15.0, 50.0)), 110.0
            imperv = float(rng.uniform(0.05, 0.30))
            slope, manning = float(rng.uniform(0.01, 0.05)), 0.04
            tide, invert = float(rng.uniform(0.0, 0.8)), 1.5
            water_prox, twi = 0.1, 0.2
            flow_len, width, drain_cap, lateral = 150.0, 30.0, None, 0.0
        elif archetype == 1:
            peak_r = float(rng.uniform(60.0, 200.0))
            r48, r120 = float(rng.uniform(150.0, 500.0)), float(rng.uniform(300.0, 900.0))
            cape, dp, wind = float(rng.uniform(2200.0, 4200.0)), -10.0, 75.0
            spi30, spi90 = 2.5, 3.0
            soil_sat = float(rng.uniform(0.85, 0.99))
            ks, psi = float(rng.uniform(0.5, 2.5)), 250.0
            imperv = float(rng.uniform(0.70, 0.92))
            slope, manning = float(rng.uniform(0.002, 0.01)), 0.018
            tide, invert = float(rng.uniform(3.2, 5.0)), 2.0
            water_prox, twi = 0.95, 0.90
            flow_len, width, drain_cap, lateral = 500.0, 40.0, 25.0, 0.25
        elif archetype == 2:
            peak_r = float(rng.uniform(70.0, 230.0))
            r48, r120 = float(rng.uniform(5.0, 30.0)), float(rng.uniform(10.0, 50.0))
            cape, dp, wind = float(rng.uniform(2500.0, 4500.0)), -12.0, 90.0
            spi30, spi90 = 0.1, -0.2
            soil_sat = float(rng.uniform(0.15, 0.35))
            ks, psi = float(rng.uniform(0.1, 1.0)), 350.0
            imperv = float(rng.uniform(0.75, 0.95))
            slope, manning = float(rng.uniform(0.001, 0.008)), 0.015
            tide, invert = float(rng.uniform(0.2, 1.0)), 1.0
            water_prox, twi = 0.25, 0.92
            flow_len, width, drain_cap, lateral = 800.0, 30.0, 5.0, 0.15
        elif archetype == 3:
            peak_r = float(rng.uniform(85.0, 215.0))
            r48, r120 = float(rng.uniform(60.0, 180.0)), float(rng.uniform(100.0, 280.0))
            cape, dp, wind = float(rng.uniform(2000.0, 3900.0)), -9.0, 60.0
            spi30, spi90 = 1.8, 2.1
            soil_sat = float(rng.uniform(0.75, 0.95))
            ks, psi = 0.05, 100.0
            imperv = float(rng.uniform(0.88, 0.99))
            slope, manning = float(rng.uniform(0.005, 0.02)), 0.012
            tide, invert = float(rng.uniform(0.5, 1.8)), 1.5
            water_prox, twi = 0.60, 0.96
            flow_len, width, drain_cap, lateral = 600.0, 30.0, 35.0, 0.25
        else:
            peak_r = float(rng.uniform(70.0, 210.0))
            r48, r120 = float(rng.uniform(40.0, 110.0)), float(rng.uniform(50.0, 150.0))
            cape, dp, wind = float(rng.uniform(1800.0, 3200.0)), -8.0, 55.0
            spi30, spi90 = 1.2, 1.5
            soil_sat = float(rng.uniform(0.80, 0.98))
            ks, psi = float(rng.uniform(2.0, 8.0)), 150.0
            imperv = float(rng.uniform(0.40, 0.65))
            slope, manning = float(rng.uniform(0.04, 0.12)), 0.035
            tide, invert = float(rng.uniform(0.0, 0.8)), 2.5
            water_prox, twi = 0.95, 0.99
            flow_len, width, drain_cap, lateral = 1200.0, 35.0, None, 12.0

        params = {
            "peak_rain_mm_hr": peak_r,
            "initial_soil_sat": soil_sat,
            "ks_mm_hr": ks,
            "psi_mm": psi,
            "impervious": imperv,
            "slope": slope,
            "manning_n": manning,
            "tide_surge_m": tide,
            "outfall_invert_m": invert,
            "flow_length_m": flow_len,
            "channel_width_m": width,
            "drain_capacity_mm_hr": drain_cap,
            "lateral_inflow_coeff": lateral,
        }
        res = sim.simulate_storm_sequence(params, horizon_hours=6, dt_sec=600.0)
        hourly_r = res["hourly_rain_mm_hr"]

        for s in range(6):
            r_hr = hourly_r[s]
            X[i, s] = [
                min(1.0, r_hr / 250.0),
                min(1.0, r48 / 500.0),
                min(1.0, r120 / 1000.0),
                min(1.0, cape / 4500.0),
                min(1.0, (dp + 15.0) / 20.0),
                min(1.0, wind / 180.0),
                min(1.0, (spi30 + 3.0) / 6.0),
                min(1.0, (spi90 + 3.0) / 6.0),
                soil_sat,
                min(1.0, ks / 50.0),
                water_prox,
                twi,
                imperv,
                min(1.0, tide / 6.0),
            ]

        Y_depth[i] = res["depth_trajectory"]
        Y_runoff[i] = [res["runoff_q"]]
        Y_prob[i] = [res["flood_prob"]]
        Y_urgency[i] = [res["urgency"]]

    if output_csv:
        with open(output_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                "r0_norm", "r48_norm", "r120_norm", "cape_norm", "dp_norm", "wind_norm",
                "spi30_norm", "spi90_norm", "soil_sat", "soil_perm", "water_prox", "twi",
                "impervious", "tide_surge_norm", "h1_cm", "h3_cm", "h6_cm", "runoff_q_m3s",
                "flash_flood_prob", "urgency_index",
            ])
            for idx in range(min(10000, n_samples)):
                row = (
                    list(X[idx, -1, :])
                    + list(Y_depth[idx])
                    + [Y_runoff[idx][0], Y_prob[idx][0], Y_urgency[idx][0]]
                )
                w.writerow(row)

    return X, Y_depth, Y_runoff, Y_prob, Y_urgency


if __name__ == "__main__":
    sim = NumericalHydrologySimulator()
    print("=== FloodLock Engine 1 v3.0 Physical Conservation Benchmark ===")
    for name, cfg in LANDMARK_BENCHMARKS.items():
        out = sim.simulate_storm_sequence(cfg)
        ma = out["mass_audit"]
        print(
            f"[{name:24s}] +1h/+3h/+6h = {out['depth_trajectory']} cm | "
            f"Peak Q = {out['runoff_q']:.2f} m3/s | Prob = {out['flood_prob']:.2f} | "
            f"Mass Residual = {ma['global_mass_residual_m']:.2e} m"
        )
