from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class Coordinates:
    lat: float
    lon: float

@dataclass
class RadiusCheckResult:
    coordinates: Coordinates
    radius_km: float
    in_danger_zone: bool
    danger_level: str
    alert_title: str
    alert_message: str
    nearest_basin: Optional[str] = None
    distance_to_basin_km: Optional[float] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RadiusCheckResult":
        coords_raw = data.get("user_coordinates", {})
        coords = Coordinates(
            lat=float(coords_raw.get("lat", 0.0)),
            lon=float(coords_raw.get("lon", 0.0))
        )
        return cls(
            coordinates=coords,
            radius_km=float(data.get("radius_km", 150.0)),
            in_danger_zone=bool(data.get("in_danger_zone", False)),
            danger_level=str(data.get("danger_level", "UNKNOWN")),
            alert_title=str(data.get("alert_title", "")),
            alert_message=str(data.get("alert_message", "")),
            nearest_basin=data.get("nearest_basin"),
            distance_to_basin_km=float(data.get("distance_to_basin_km", 0.0)) if data.get("distance_to_basin_km") is not None else None,
            raw=data
        )

@dataclass
class ForecastResult:
    coordinates: Coordinates
    risk_score: float
    threat_level: str
    discharge_m3s: Optional[float] = None
    soil_saturation_pct: Optional[float] = None
    outfall_head_m: Optional[float] = None
    safety_floor_triggered: bool = False
    model_version: str = "70B-Ensemble-v2.4"
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ForecastResult":
        coords_raw = data.get("coordinates", {})
        coords = Coordinates(
            lat=float(coords_raw.get("lat", 0.0)),
            lon=float(coords_raw.get("lon", 0.0))
        )
        return cls(
            coordinates=coords,
            risk_score=float(data.get("risk_score", 0.0)),
            threat_level=str(data.get("threat_level", "NOMINAL")),
            discharge_m3s=float(data.get("discharge_m3s", 0.0)) if data.get("discharge_m3s") is not None else None,
            soil_saturation_pct=float(data.get("soil_saturation_pct", 0.0)) if data.get("soil_saturation_pct") is not None else None,
            outfall_head_m=float(data.get("outfall_head_m", 0.0)) if data.get("outfall_head_m") is not None else None,
            safety_floor_triggered=bool(data.get("safety_floor_triggered", False)),
            model_version=str(data.get("model_version", "70B-Ensemble-v2.4")),
            raw=data
        )
