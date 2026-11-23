"""
physics/test_physics_conservation.py
Automated Physical Conservation & Edge-Case Verification Suite for Engine 1.
"""

import unittest
from floodlock_physics_simulator import LANDMARK_BENCHMARKS, NumericalHydrologySimulator


class TestFloodLockPhysicsConservation(unittest.TestCase):
    def setUp(self):
        self.sim = NumericalHydrologySimulator()

    def test_sahara_zero_rain_zero_hallucination(self):
        res = self.sim.simulate_storm_sequence(LANDMARK_BENCHMARKS["sahara_control"])
        self.assertEqual(res["depth_trajectory"], [0.0, 0.0, 0.0])
        self.assertEqual(res["runoff_q"], 0.0)
        self.assertEqual(res["flood_prob"], 0.0)
        self.assertLess(res["mass_audit"]["global_mass_residual_m"], 1e-12)

    def test_mumbai_extreme_spring_tide_no_blowup(self):
        res = self.sim.simulate_storm_sequence(LANDMARK_BENCHMARKS["mumbai_2005_deluge"])
        ma = res["mass_audit"]
        self.assertGreater(res["peak_depth_cm"], 50.0)
        self.assertLess(res["peak_depth_cm"], 300.0)
        self.assertGreater(res["flood_prob"], 0.80)
        self.assertLess(ma["global_mass_residual_m"], 1e-9)
        self.assertLessEqual(ma["final_depth_m"], ma["cum_inflow_m"] + ma["cum_backwater_m"] + 1e-9)

    def test_dubai_cloudburst_severe_ponding(self):
        res = self.sim.simulate_storm_sequence(LANDMARK_BENCHMARKS["dubai_2024_cloudburst"])
        self.assertGreater(res["peak_depth_cm"], 30.0)
        self.assertLess(res["mass_audit"]["global_mass_residual_m"], 1e-9)

    def test_valencia_barranco_violent_flash_discharge(self):
        res = self.sim.simulate_storm_sequence(LANDMARK_BENCHMARKS["valencia_2024_barranco"])
        self.assertGreater(res["runoff_q"], 30.0)
        self.assertGreater(res["flood_prob"], 0.85)
        self.assertLess(res["mass_audit"]["global_mass_residual_m"], 1e-9)
        for d in res["depth_trajectory"]:
            self.assertGreaterEqual(d, 0.0)

    def test_extreme_10m_tsunami_surge_hydrostatic_equilibrium(self):
        state = {
            "rain_rate_mm_hr": 0.0, "soil_sat": 0.99, "ks_mm_hr": 0.0,
            "psi_mm": 100.0, "impervious": 1.0, "slope": 0.001, "manning_n": 0.02,
            "tide_surge_m": 10.0, "outfall_invert_m": 2.0, "depth_m": 0.0, "cum_infil_mm": 0.0,
        }
        for _ in range(200):
            out = self.sim.solve_timestep(state, dt_sec=600.0)
            state["depth_m"] = out["depth_m"]
            state["cum_infil_mm"] = out["cum_infil_mm"]
            self.assertGreaterEqual(state["depth_m"], 0.0)
            self.assertLessEqual(state["depth_m"], 8.0 + 1e-9)
            self.assertLess(out["mass_residual_m"], 1e-10)

    def test_ponded_water_drains_and_infiltrates_after_rain_stops(self):
        state = {
            "rain_rate_mm_hr": 0.0, "soil_sat": 0.30, "ks_mm_hr": 25.0,
            "psi_mm": 120.0, "impervious": 0.40, "slope": 0.02, "manning_n": 0.03,
            "tide_surge_m": 0.5, "outfall_invert_m": 2.0, "depth_m": 0.20, "cum_infil_mm": 0.0,
            "flow_length_m": 100.0, "drain_capacity_mm_hr": None,
        }
        prev_h = state["depth_m"]
        for _ in range(18):
            out = self.sim.solve_timestep(state, dt_sec=600.0)
            self.assertGreaterEqual(out["depth_m"], 0.0)
            self.assertLessEqual(out["depth_m"], prev_h + 1e-12)
            self.assertLess(out["mass_residual_m"], 1e-10)
            prev_h = out["depth_m"]
            state["depth_m"] = out["depth_m"]
            state["cum_infil_mm"] = out["cum_infil_mm"]
        self.assertLess(state["depth_m"], 0.05)


if __name__ == "__main__":
    unittest.main(verbosity=2)
