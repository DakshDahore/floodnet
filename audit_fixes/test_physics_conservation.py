"""Run: python test_physics_conservation.py   (no dependencies)"""
import random
from floodlock_physics_fixed import Basin, HydrologyEngine, MassBalanceError, heuristic_risk

E = HydrologyEngine()


def coastal_dry(**kw):
    d = dict(ks_mm_hr=30, psi_mm=110, initial_soil_sat=0.2, impervious=0.1,
             slope=0.02, manning_n=0.04, tide_m=4.48, outfall_invert_m=1.5)
    d.update(kw)
    return Basin(**d)


def test_zero_rain_high_tide_is_exactly_zero():
    # The original simulator produced 1.5 cm here (water created from nothing).
    r = E.simulate_storm(coastal_dry(), peak_rain_mm_hr=0.0)
    assert all(x == 0.0 for x in r["depth_series_cm"]), r["depth_series_cm"]
    assert r["ledger_m"]["backwater_in_m"] == 0.0


def test_sahara_control():
    b = Basin(ks_mm_hr=40, psi_mm=110, initial_soil_sat=0.1, impervious=0.05,
              slope=0.02, manning_n=0.04)
    r = E.simulate_storm(b, 0.0)
    assert r["targets_cm"] == {"+1h": 0.0, "+3h": 0.0, "+6h": 0.0}


def test_mass_balance_and_bounds_random():
    rnd = random.Random(1234)
    for _ in range(1500):
        b = Basin(
            ks_mm_hr=rnd.uniform(0.01, 60), psi_mm=rnd.uniform(50, 400),
            initial_soil_sat=rnd.uniform(0, 1), impervious=rnd.uniform(0, 1),
            slope=rnd.uniform(0.001, 0.15), manning_n=rnd.uniform(0.01, 0.1),
            flow_length_m=rnd.uniform(20, 500), tide_m=rnd.uniform(0, 5.5),
            outfall_invert_m=rnd.uniform(0.5, 2.5),
        )
        r = E.simulate_storm(b, rnd.uniform(0, 250), duration_hr=rnd.uniform(0.5, 6))
        assert abs(r["mass_balance_residual_m"]) < 1e-9
        assert min(r["depth_series_cm"]) >= 0.0
        led = r["ledger_m"]
        # depth can never exceed everything that ever entered
        max_in = led["rain_in_m"] + led["backwater_in_m"]
        assert max(r["depth_series_cm"]) / 100.0 <= max_in + 1e-12


def test_horizons_are_real_time():
    r = E.simulate_storm(coastal_dry(), 80.0, duration_hr=3.0, horizon_hr=6.0, report_every_s=600)
    assert len(r["depth_series_cm"]) == 36          # 6 h / 10 min
    s = r["depth_series_cm"]
    assert r["targets_cm"] == {"+1h": s[5], "+3h": s[17], "+6h": s[35]}


def test_choke_never_reduces_depth():
    base = dict(ks_mm_hr=1.0, psi_mm=250, initial_soil_sat=0.95, impervious=0.85,
                slope=0.004, manning_n=0.018, outfall_invert_m=1.5)
    lo = E.simulate_storm(Basin(tide_m=0.5, **base), 150.0)["targets_cm"]["+3h"]
    hi = E.simulate_storm(Basin(tide_m=4.48, **base), 150.0)["targets_cm"]["+3h"]
    assert hi >= lo, (lo, hi)


def test_backwater_bounded_by_reservoir():
    b = Basin(ks_mm_hr=1.0, psi_mm=250, initial_soil_sat=0.95, impervious=0.85,
              slope=0.004, manning_n=0.018, tide_m=4.48, tidal_reservoir_m=0.01)
    r = E.simulate_storm(b, 150.0)
    assert r["ledger_m"]["backwater_in_m"] <= 0.01 + 1e-12


def test_invalid_inputs_rejected():
    for bad in (dict(impervious=1.2), dict(manning_n=0), dict(initial_soil_sat=-0.1)):
        try:
            coastal_dry(**bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted bad input {bad}")


def test_mass_error_detects_tampering():
    # Sanity check that the guard is live: break the ledger and expect a raise.
    class Broken(HydrologyEngine):
        def step(self, b, s, rain, dt):
            super().step(b, s, rain, dt)
            s.h_m += 1e-6          # inject mass
    try:
        Broken().simulate_storm(coastal_dry(), 50.0)
    except MassBalanceError:
        return
    raise AssertionError("mass guard did not fire")


def test_heuristic_is_labelled():
    assert heuristic_risk({"+3h": 40}, 0)["basis"] == "heuristic"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fns:
        f()
        print("PASS", f.__name__)
    print(f"\n{len(fns)} tests passed")
