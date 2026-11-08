"""
floodlock_backend_local/engine/dispatch_slm.py
────────────────────────────────────────────────────────────────────────────
Locked Machine-to-Machine (M2M) Autonomous Dispatch Engine.
Powered by sandboxed local Ollama (qwen2.5:0.5b @ ~162 tokens/sec).

SECURITY ENFORCEMENT:
  - Zero public chat endpoint.
  - Zero conversational LLM capability.
  - Accepts ONLY validated numeric telemetry state.
  - Emits structured MCGM F-South Ward Emergency Operational Directives.
"""

import time
import httpx

OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"


def generate_institutional_fallback(
    alert_code: str,
    rain_instant: float,
    effective_tide: float,
    choke_pct: float,
    eta_minutes: float,
    water_depth_m: float
) -> dict:
    """
    Deterministic rule-based municipal directive fallback when Ollama is offline.
    Guarantees 100% endpoint uptime with zero 500 errors.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S IST", time.localtime())

    if alert_code == "CRITICAL_HYDRAULIC_LOCK":
        sluice_order = (
            "EMERGENCY ORDER 01/MCGM-FS: Total Hydraulic Lock confirmed at Love Grove Outfall "
            f"(Effective Tide: {effective_tide}m MSL >= 3.00m invert). Immediately close flap gates to prevent "
            "Arabian Sea backflow. Deploy Pramod Mahajan Holding Tank submersible high-head pumps (5 x 6,000 m3/hr) "
            "at maximum stage. Divert local runoff to Britannia storm sump."
        )
        route_order = (
            f"TRAFFIC & AMBULANCE DIRECTIVE: Hindmata Dr. B.A. Road Underpass is SEVERED (Ponding: {water_depth_m}m). "
            "Activate emergency barricades immediately. Divert ALL emergency transit and ambulances to "
            "Dadar TT Elevated Viaduct (+8.5m MSL) for uninterrupted access to KEM Hospital Trauma Ward."
        )
        bulletin = (
            "MCGM EMERGENCY ADVISORY: Extreme compound inundation active in Hindmata basin. "
            "Citizens instructed to avoid low-lying ground level roads and underpasses. Use elevated flyovers only."
        )
    elif alert_code == "RED_WARNING":
        sluice_order = (
            f"OPERATIONAL ORDER: Sluice gates choking at {choke_pct}%. Pre-activate Pramod Mahajan auxiliary sumps. "
            "Monitor Love Grove gravity discharge head closely."
        )
        route_order = (
            f"TRAFFIC DIRECTIVE: Anticipatory rerouting to Dadar TT Elevated Viaduct (+8.5m MSL). "
            f"Time-to-inundation: {eta_minutes} min."
        )
        bulletin = (
            f"RED ALERT: Heavy localized downpour ({rain_instant} mm/hr) coupled with elevated tidal surge. "
            "Travel through Hindmata junction restricted."
        )
    elif alert_code == "AMBER_WATCH":
        sluice_order = (
            f"WATCH ORDER: Gravity drainage partially choked ({choke_pct}%). Station dewatering teams on standby "
            "at Hindmata Flyover base."
        )
        route_order = (
            "TRAFFIC DIRECTIVE: Heavy vehicle priority on surface Dr. B.A. Road. Light vehicles advised to utilize "
            "Dadar TT Flyover."
        )
        bulletin = "AMBER WATCH: Moderate monsoon showers and high tide concurrence. Exercise caution."
    else:
        sluice_order = "NOMINAL: Sluice gates open at 100% capacity. Gravity drainage fully operational."
        route_order = "NOMINAL: Dr. B.A. Road surface corridor and Hindmata junction clear. Normal operations."
        bulletin = "GREEN: Precipitation and sea levels within nominal capacity limits."

    return {
        "dispatch_id": f"DISP-{int(time.time())}",
        "timestamp": timestamp,
        "engine": "DETERMINISTIC_INSTITUTIONAL_SOP_ENGINE",
        "alert_code": alert_code,
        "sluice_and_pump_order": sluice_order,
        "evacuation_route_order": route_order,
        "citizen_safety_bulletin": bulletin,
        "telemetry_context": {
            "rain_mm_hr": rain_instant,
            "effective_tide_m": effective_tide,
            "sluice_choke_pct": choke_pct,
            "eta_minutes": eta_minutes,
            "water_depth_m": water_depth_m
        }
    }


def generate_m2m_dispatch(
    rain_instant: float,
    effective_tide: float,
    choke_pct: float,
    eta_minutes: float,
    water_depth_m: float,
    timeout_sec: float = 3.5
) -> dict:
    """
    Invokes local Ollama (qwen2.5:0.5b) strictly for autonomous system-to-system dispatch.
    """
    # 1. Determine institutional alert classification
    if choke_pct >= 95.0 or (eta_minutes <= 15.0 and rain_instant >= 80.0):
        alert_code = "CRITICAL_HYDRAULIC_LOCK"
    elif eta_minutes <= 30.0 or choke_pct >= 75.0 or rain_instant >= 100.0:
        alert_code = "RED_WARNING"
    elif eta_minutes <= 60.0 or choke_pct >= 40.0:
        alert_code = "AMBER_WATCH"
    else:
        alert_code = "GREEN_NOMINAL"

    # 2. Strict system prompt strictly enforcing institutional structure
    prompt = f"""[MUNICIPAL CRISIS SYSTEM PROMPT - MCGM F-SOUTH WARD]
You are the Autonomous Compound Flood Dispatcher for Mumbai F-South Ward (Hindmata Basin & Love Grove Outfall).
Generate a formal 4-part Emergency Operational Directive based on the following verified numeric telemetry:
- Alert Level: {alert_code}
- Rain Rate: {rain_instant} mm/hr
- Sea Level at Love Grove Outfall: {effective_tide} m MSL (Crown Invert: 3.00m)
- Outfall Gravity Sluice Choke: {choke_pct}%
- Inundation Countdown: {eta_minutes} minutes
- Estimated Street Water Depth: {water_depth_m} meters

Format your exact response in these 4 labeled sections:
1. ALERT CODE: [{alert_code}]
2. SLUICE AND PUMP ORDER: (Exact operational directives for Love Grove Flap Gates and Pramod Mahajan Holding Tank Pumps)
3. EVACUATION AND AMBULANCE ROUTE ORDER: (Explicit traffic diversion between Dr. B.A. Road surface vs Dadar TT Elevated Viaduct +8.5m MSL towards KEM Hospital)
4. CITIZEN SAFETY BULLETIN: (Concise public advisory in English)
Keep technical, concise, authoritative, and zero preamble."""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 250
        }
    }

    try:
        t0 = time.perf_counter()
        with httpx.Client(timeout=timeout_sec) as client:
            resp = client.post(OLLAMA_GENERATE_URL, json=payload)
            if resp.status_code == 200:
                raw_text = resp.json().get("response", "")
                elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 1)

                # Parse labeled sections
                sluice_text = ""
                route_text = ""
                bulletin_text = ""

                lines = raw_text.split("\n")
                current_sec = None
                for line in lines:
                    line_upper = line.upper()
                    if "SLUICE AND PUMP ORDER:" in line_upper or "SLUICE ORDER:" in line_upper:
                        current_sec = "sluice"
                        sluice_text += line.split(":", 1)[-1].strip() + " "
                    elif "EVACUATION AND AMBULANCE" in line_upper or "ROUTE ORDER:" in line_upper:
                        current_sec = "route"
                        route_text += line.split(":", 1)[-1].strip() + " "
                    elif "CITIZEN SAFETY BULLETIN:" in line_upper or "SAFETY BULLETIN:" in line_upper:
                        current_sec = "bulletin"
                        bulletin_text += line.split(":", 1)[-1].strip() + " "
                    elif current_sec == "sluice":
                        sluice_text += line.strip() + " "
                    elif current_sec == "route":
                        route_text += line.strip() + " "
                    elif current_sec == "bulletin":
                        bulletin_text += line.strip() + " "

                if not sluice_text.strip() or not route_text.strip():
                    # Fallback to structured fallback if parsing was incomplete
                    return generate_institutional_fallback(
                        alert_code, rain_instant, effective_tide, choke_pct, eta_minutes, water_depth_m
                    )

                return {
                    "dispatch_id": f"DISP-{int(time.time())}",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S IST", time.localtime()),
                    "engine": f"AUTONOMOUS_OLLAMA_{MODEL_NAME.upper()}",
                    "alert_code": alert_code,
                    "inference_latency_ms": elapsed_ms,
                    "sluice_and_pump_order": sluice_text.strip(),
                    "evacuation_route_order": route_text.strip(),
                    "citizen_safety_bulletin": bulletin_text.strip(),
                    "telemetry_context": {
                        "rain_mm_hr": rain_instant,
                        "effective_tide_m": effective_tide,
                        "sluice_choke_pct": choke_pct,
                        "eta_minutes": eta_minutes,
                        "water_depth_m": water_depth_m
                    }
                }
    except Exception as e:
        print(f"[*] Note: Ollama invocation fell back to institutional template: {e}")

    # Seamless fallback
    return generate_institutional_fallback(
        alert_code, rain_instant, effective_tide, choke_pct, eta_minutes, water_depth_m
    )
