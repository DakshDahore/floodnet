"""
floodlock_backend_local/engine/state_cache.py
────────────────────────────────────────────────────────────────────────────
Temporal Hydrology State Cache & Antecedent Flood Memory Engine.
Preserves rolling water logging history, antecedent soil saturation, and 
cumulative standing water across storm bursts so the AI never forgets 
pre-existing street water depth (e.g. 14 cm ponding before new rain arrives).
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "temporal_state_cache.json")


class TemporalStateCache:
    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = cache_file
        self.standing_water_depth_m: float = 0.0  # Current standing ponding depth in meters
        self.cumulative_rain_6hr_mm: float = 0.0
        self.last_update_ts: float = time.time()
        self.history: List[Dict[str, Any]] = []
        self.max_history_entries: int = 72  # 12 hours of 10-minute records
        self.load()

    def load(self):
        """Loads state from disk if available."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.standing_water_depth_m = float(data.get("standing_water_depth_m", 0.0))
                    self.cumulative_rain_6hr_mm = float(data.get("cumulative_rain_6hr_mm", 0.0))
                    self.last_update_ts = float(data.get("last_update_ts", time.time()))
                    self.history = data.get("history", [])
            except Exception as e:
                print(f"[WARN] Failed to load temporal state cache: {e}")
                self.reset()
        else:
            self.reset()

    def save(self):
        """Persists state to disk."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({
                    "standing_water_depth_m": round(self.standing_water_depth_m, 4),
                    "standing_water_depth_cm": round(self.standing_water_depth_m * 100.0, 1),
                    "cumulative_rain_6hr_mm": round(self.cumulative_rain_6hr_mm, 2),
                    "last_update_ts": self.last_update_ts,
                    "last_update_iso": datetime.fromtimestamp(self.last_update_ts).isoformat(),
                    "history_count": len(self.history),
                    "history": self.history[-self.max_history_entries:]
                }, f, indent=2)
        except Exception as e:
            print(f"[WARN] Failed to save temporal state cache: {e}")

    def reset(self):
        """Resets water logging memory to zero (dry baseline)."""
        self.standing_water_depth_m = 0.0
        self.cumulative_rain_6hr_mm = 0.0
        self.last_update_ts = time.time()
        self.history = []
        self.save()

    def update_step(
        self,
        rain_instant_mm: float,
        effective_rain_mm: float,
        q_drain_mm: float,
        choke_pct: float,
        dt_minutes: float = 10.0
    ) -> Dict[str, Any]:
        """
        Calculates new standing water depth accounting for antecedent ponding.
        dt_minutes: time interval elapsed since previous step (default 10 mins).
        """
        now = time.time()
        hours_elapsed = max(0.01, (now - self.last_update_ts) / 3600.0) if self.last_update_ts else (dt_minutes / 60.0)
        dt_hours = dt_minutes / 60.0

        # Inflow vs Drainage
        q_inflow = effective_rain_mm
        delta_q = q_inflow - q_drain_mm

        # Water depth change in meters
        # In Hindmata saucer: 50 mm/hr net accumulation adds ~0.35m of street depth per hour
        if delta_q > 0:
            depth_delta = (delta_q / 50.0) * 0.35 * dt_hours
        else:
            # Gravity drainage recession: street empties at max 0.15m per hour when drain > inflow
            recession_rate = min(0.20, (abs(delta_q) / 25.0) * 0.15)
            depth_delta = -1.0 * recession_rate * dt_hours

        # Update standing ponding depth with floor at 0.0m and physical maximum at 1.85m
        old_depth = self.standing_water_depth_m
        self.standing_water_depth_m = max(0.0, min(1.85, old_depth + depth_delta))

        # Update cumulative rolling rain
        decay_factor = max(0.0, 1.0 - (dt_hours / 6.0))
        self.cumulative_rain_6hr_mm = self.cumulative_rain_6hr_mm * decay_factor + (rain_instant_mm * dt_hours)
        self.last_update_ts = now

        entry = {
            "timestamp": now,
            "iso": datetime.fromtimestamp(now).strftime("%H:%M:%S"),
            "rain_mm_hr": round(rain_instant_mm, 1),
            "effective_rain_mm_hr": round(effective_rain_mm, 1),
            "q_drain_mm_hr": round(q_drain_mm, 1),
            "choke_pct": round(choke_pct, 1),
            "water_depth_m": round(self.standing_water_depth_m, 3),
            "water_depth_cm": round(self.standing_water_depth_m * 100.0, 1)
        }
        self.history.append(entry)
        if len(self.history) > self.max_history_entries:
            self.history.pop(0)

        self.save()

        return {
            "antecedent_depth_m": round(old_depth, 3),
            "current_standing_depth_m": round(self.standing_water_depth_m, 3),
            "current_standing_depth_cm": round(self.standing_water_depth_m * 100.0, 1),
            "cumulative_rain_6hr_mm": round(self.cumulative_rain_6hr_mm, 1),
            "is_waterlogged": self.standing_water_depth_m >= 0.10,
            "is_severely_inundated": self.standing_water_depth_m >= 0.30
        }

    def get_state(self) -> Dict[str, Any]:
        """Returns the current temporal state."""
        return {
            "standing_water_depth_m": round(self.standing_water_depth_m, 3),
            "standing_water_depth_cm": round(self.standing_water_depth_m * 100.0, 1),
            "cumulative_rain_6hr_mm": round(self.cumulative_rain_6hr_mm, 1),
            "last_update_iso": datetime.fromtimestamp(self.last_update_ts).isoformat(),
            "history_count": len(self.history),
            "is_waterlogged": self.standing_water_depth_m >= 0.10,
            "is_severely_inundated": self.standing_water_depth_m >= 0.30,
            "recent_history": self.history[-12:]
        }


# Global Singleton
temporal_cache = TemporalStateCache()
