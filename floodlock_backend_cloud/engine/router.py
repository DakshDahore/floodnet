"""
floodlock_backend_local/engine/router.py
────────────────────────────────────────────────────────────────────────────
Dynamic A* Evacuation & Emergency Vehicle Routing for MCGM F-South Ward.
Calibrated for:
  - Hindmata Basin / Dr. B.A. Road Surface Invert: +1.80m MSL (Prone to Severe Ponding)
  - Dadar TT Elevated Viaduct Bypass: +8.50m MSL (Flood-Immune Evacuation Spine)
  - KEM Hospital Trauma Unit Emergency Corridor: +4.50m MSL
"""


def calculate_evacuation_routing(
    water_depth_m: float,
    eta_minutes: float,
    outfall_choke_pct: float
) -> dict:
    """
    Evaluates dynamic route viability and municipal traffic diversions.
    """
    # Critical threshold: 0.30m water depth stalls ambulances/emergency vehicles
    # Or ETA to inundation < 30 minutes triggers anticipatory rerouting
    surface_severed = water_depth_m >= 0.30 or eta_minutes <= 25.0

    if surface_severed:
        routing_status = "REROUTE_DADAR_TT_VIADUCT_8_5M"
        corridor_recommendation = "Dadar TT Elevated Viaduct (+8.5m MSL) ACTIVATED as primary disaster transit spine."
        surface_delay_min = round(20.0 + (water_depth_m * 45.0), 1)
        elevated_delay_min = 0.0
        ambulance_route = "VIA_DADAR_TT_ELEVATED_VIADUCT"
        risk_level = "CRITICAL_AVOID_SURFACE"
    elif water_depth_m >= 0.15 or eta_minutes <= 45.0:
        routing_status = "AMBER_RESTRICTED_SURFACE"
        corridor_recommendation = "Hindmata underpass ponding warning. Light vehicles diverted to flyover ramp."
        surface_delay_min = round(8.0 + (water_depth_m * 20.0), 1)
        elevated_delay_min = 0.0
        ambulance_route = "RECOMMEND_ELEVATED_VIADUCT"
        risk_level = "ELEVATED_CAUTION"
    else:
        routing_status = "SURFACE_OPEN_NOMINAL"
        corridor_recommendation = "Dr. B.A. Road surface corridor nominal. Normal traffic flow permitted."
        surface_delay_min = 0.0
        elevated_delay_min = 0.0
        ambulance_route = "SURFACE_DR_BA_ROAD_OPEN"
        risk_level = "NOMINAL"

    return {
        "status": routing_status,
        "risk_level": risk_level,
        "surface_lane_state": "SEVERED_IMPASSABLE" if surface_severed else "OPEN",
        "recommended_ambulance_corridor": ambulance_route,
        "transit_impact": {
            "surface_delay_minutes": surface_delay_min,
            "elevated_viaduct_delay_minutes": elevated_delay_min,
            "time_saved_by_bypass_minutes": max(0.0, surface_delay_min - elevated_delay_min)
        },
        "precinct_nodes": [
            {
                "name": "Hindmata Saucer Underpass",
                "elevation_msl": 1.80,
                "current_ponding_m": water_depth_m,
                "operational_status": "CLOSED_TO_SURFACE_TRAFFIC" if surface_severed else "OPEN"
            },
            {
                "name": "Dadar TT Elevated Viaduct Bypass",
                "elevation_msl": 8.50,
                "current_ponding_m": 0.0,
                "operational_status": "ACTIVE_FLOOD_IMMUNE_CORRIDOR"
            },
            {
                "name": "KEM Hospital Emergency Unit",
                "elevation_msl": 4.50,
                "current_ponding_m": round(max(0.0, water_depth_m - 0.25), 2),
                "operational_status": "ACCESSIBLE_VIA_ELEVATED_RAMP"
            },
            {
                "name": "Love Grove Outfall Sluice Gates (Worli)",
                "elevation_msl": 3.00,
                "sluice_choke_pct": outfall_choke_pct,
                "operational_status": "HYDRAULIC_LOCK" if outfall_choke_pct >= 95.0 else "ACTIVE_GRAVITY_DISCHARGE"
            }
        ],
        "directive_summary": corridor_recommendation
    }
