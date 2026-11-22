"""
floodlock_physics_fixed.py
─────────────────────────────────────────────────────────────────────────────
Engine 1 (corrected): a lumped, unit-consistent overland-flow model with an
explicit MASS LEDGER. Every cubic metre is accounted for, and the run raises
MassBalanceError if conservation is violated.

What changed vs. the original floodlock_physics_simulator.py
  1. Backwater inflow is no longer a free constant. It only occurs when the
     surface is already ponded (surcharged), and it draws from a FINITE
     tidal reservoir that depletes. Zero rain + high tide => exactly 0.0 cm.
  2. Manning discharge is per-metre-width (m^2/s) and converted to a depth
     change through an explicit flow length L (no magic "/100" or "*10").
  3. Green-Ampt capacity is limited by the water actually available and
     uses a floored F (no "Ks*8" hack). Ponded water on pervious area infiltrates.
  4. Depression storage is a real state (water below it does not flow), not a
     cosmetic subtraction applied only to the reported number.
  5. Horizons are what they say: +1h, +3h, +6h of simulated time.
  6. Sub-stepping (default 60 s) plus clamping keeps the explicit scheme stable
     and non-negative.

Scope (be honest about it): this is a LUMPED single-cell model, not the 2D
Saint-Venant equations. The flood probability helper is a HEURISTIC label, not
physics. Calibration against observed gauges/inundation maps is still required
before any claim of "calibrated to real disasters".
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

MM = 1e-3


class MassBalanceError(AssertionError):
    pass


@dataclass
class Basin:
    ks_mm_hr: float            # saturated hydraulic conductivity
    psi_mm: float              # wetting-front suction head
    initial_soil_sat: float    # 0..1
    impervious: float          # 0..1 fraction of cell that cannot infiltrate
    slope: float               # m/m
    manning_n: float
    flow_length_m: float = 100.0       # path length surface water travels to the outlet
    outlet_width_m: float = 10.0       # used only to report discharge in m^3/s
    depression_storage_m: float = 0.005
    tide_m: float = 0.0
    outfall_invert_m: float = 1.5
    choke_span_m: float = 1.5          # head above invert at which the outfall is fully choked
    max_choke: float = 0.90            # max fractional drainage suppression
    tidal_reservoir_m: float = 0.02    # finite depth-equivalent seawater that can push back
    backflow_rate_m_hr: float = 0.02   # max push-back rate at full choke

    def __post_init__(self):
        if not (0.0 <= self.impervious <= 1.0):
            raise ValueError("impervious must be in [0,1]")
        if not (0.0 <= self.initial_soil_sat <= 1.0):
            raise ValueError("initial_soil_sat must be in [0,1]")
        for name in ("ks_mm_hr", "psi_mm", "slope", "manning_n", "flow_length_m"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be > 0")


@dataclass
class Ledger:
    rain_in_m: float = 0.0
    backwater_in_m: float = 0.0
    infiltrated_m: float = 0.0
    drained_m: float = 0.0
    initial_storage_m: float = 0.0

    def residual(self, final_storage_m: float) -> float:
        inflow = self.rain_in_m + self.backwater_in_m
        outflow = self.infiltrated_m + self.drained_m
        return (self.initial_storage_m + inflow - outflow) - final_storage_m


@dataclass
class State:
    h_m: float = 0.0                 # total surface storage (incl. depression storage), cell-average
    cum_infil_mm: float = 0.0        # Green-Ampt F, per PERVIOUS area
    reservoir_m: float = 0.0
    last_q_m3s: float = 0.0
    ledger: Ledger = field(default_factory=Ledger)


class HydrologyEngine:
    def step(self, b: Basin, s: State, rain_mm_hr: float, dt: float) -> None:
        rain_m = max(0.0, rain_mm_hr) * MM / 3600.0 * dt
        s.ledger.rain_in_m += rain_m
        avail = s.h_m + rain_m                         # water on the surface this step

        # Green-Ampt infiltration on the pervious fraction, limited by available water
        pervious = 1.0 - b.impervious
        d_theta = max(0.05, 0.45 * (1.0 - b.initial_soil_sat))
        F = max(s.cum_infil_mm, 0.1)                   # floor avoids division by zero
        cap_m = b.ks_mm_hr * (1.0 + b.psi_mm * d_theta / F) * MM / 3600.0 * dt
        per_area_m = min(cap_m, avail)                 # per pervious area
        infil_m = pervious * per_area_m                # cell-average
        s.cum_infil_mm += per_area_m / MM
        s.ledger.infiltrated_m += infil_m
        h = avail - infil_m

        # Manning sheet flow on the mobile water above depression storage
        mobile = max(0.0, h - b.depression_storage_m)
        q = (1.0 / b.manning_n) * mobile ** (5.0 / 3.0) * math.sqrt(b.slope)  # m^2/s (Rh ~ h)

        choke = 0.0
        if b.tide_m > b.outfall_invert_m:
            choke = min(1.0, (b.tide_m - b.outfall_invert_m) / b.choke_span_m)
        q *= (1.0 - b.max_choke * choke)

        drain_m = min(mobile, q * dt / b.flow_length_m)  # can never remove more than exists
        s.ledger.drained_m += drain_m
        s.last_q_m3s = q * b.outlet_width_m
        h -= drain_m

        # Tidal push-back: only if surcharged, and only from a finite reservoir
        bw_m = 0.0
        if choke > 0.0 and mobile > 0.0 and s.reservoir_m > 0.0:
            bw_m = min(s.reservoir_m, b.backflow_rate_m_hr * choke * dt / 3600.0)
            s.reservoir_m -= bw_m
            s.ledger.backwater_in_m += bw_m
            h += bw_m

        s.h_m = max(0.0, h)   # only guards float dust; real negatives are impossible above

    def simulate_storm(
        self,
        b: Basin,
        peak_rain_mm_hr: float,
        duration_hr: float = 3.0,
        horizon_hr: float = 6.0,
        dt_s: float = 60.0,
        report_every_s: float = 600.0,
        tol_m: float = 1e-9,
    ) -> dict:
        s = State(reservoir_m=b.tidal_reservoir_m)
        n = int(round(horizon_hr * 3600.0 / dt_s))
        per_report = max(1, int(round(report_every_s / dt_s)))
        series_cm, peak_q = [], 0.0
        for i in range(n):
            t = (i + 0.5) * dt_s
            frac = math.sin(math.pi * t / (duration_hr * 3600.0)) if t < duration_hr * 3600.0 else 0.0
            self.step(b, s, peak_rain_mm_hr * max(0.0, frac), dt_s)
            peak_q = max(peak_q, s.last_q_m3s)
            if (i + 1) % per_report == 0:
                series_cm.append(round(max(0.0, s.h_m - b.depression_storage_m) * 100.0, 3))

        resid = s.ledger.residual(s.h_m)
        if abs(resid) > tol_m:
            raise MassBalanceError(f"mass balance residual {resid:.3e} m exceeds {tol_m:.1e}")

        def at(hours: float) -> float:
            idx = int(round(hours * 3600.0 / report_every_s)) - 1
            return series_cm[min(idx, len(series_cm) - 1)]

        return {
            "depth_series_cm": series_cm,
            "targets_cm": {"+1h": at(1.0), "+3h": at(3.0), "+6h": at(6.0)},
            "peak_q_m3s": round(peak_q, 4),
            "mass_balance_residual_m": resid,
            "ledger_m": s.ledger.__dict__.copy(),
            "final_storage_m": s.h_m,
        }


def heuristic_risk(targets_cm: dict, peak_q_m3s: float) -> dict:
    """HEURISTIC label only - thresholds are placeholders for a domain authority to set."""
    h3 = targets_cm["+3h"]
    if h3 > 30.0:
        return {"label": "SEVERE", "basis": "heuristic"}
    if h3 > 5.0 or peak_q_m3s > 5.0:
        return {"label": "ELEVATED", "basis": "heuristic"}
    return {"label": "LOW", "basis": "heuristic"}
