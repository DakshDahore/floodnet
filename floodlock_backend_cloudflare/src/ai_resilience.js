/**
 * cloudflare_worker/src/ai_resilience.js
 * ============================================================================
 * FloodLock v3.2 Gold — 3-Tier Distributed Tactical AI Reasoning Engine:
 *  - Tier 1: Groq LPU Qwen (env.GROQ_MODEL, reasoning_effort: "none", 2500ms)
 *  - Tier 2: Google Cloud Gemini GA Flash (env.GEMINI_MODEL, thinkingLevel: "low",
 *    x-goog-api-key header, 3500ms)
 *  - Tier 3: Deterministic V8 Edge Hydrological SOP + Life-Safety Hazard Guard
 *  - Anti-Cache-Poisoning: Custom what-if simulations bypass shared KV cache.
 */

async function fetchWithTimeout(url, options, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

function normalizeTacticalPayload(raw, engineLabel, fallbackObj) {
  if (!raw || typeof raw !== "object") return fallbackObj;

  let status = fallbackObj.verification_status;
  if (fallbackObj.verification_status === "VERIFIED_FLOOD_HAZARD") {
    status = "VERIFIED_FLOOD_HAZARD";
  } else if (
    raw.verification_status === "VERIFIED_FLOOD_HAZARD" ||
    raw.verification_status === "FALSE_ALARM_DOWNGRADED"
  ) {
    status = raw.verification_status;
  }

  return {
    engine: engineLabel,
    verification_status: status,
    confidence_score: Number.isFinite(Number(raw.confidence_score))
      ? Math.max(1, Math.min(100, Math.round(Number(raw.confidence_score))))
      : fallbackObj.confidence_score,
    causal_attribution:
      typeof raw.causal_attribution === "string" && raw.causal_attribution.length > 5
        ? raw.causal_attribution.slice(0, 400)
        : fallbackObj.causal_attribution,
    danger_zone_perimeter:
      typeof raw.danger_zone_perimeter === "string" && raw.danger_zone_perimeter.length > 5
        ? raw.danger_zone_perimeter.slice(0, 300)
        : fallbackObj.danger_zone_perimeter,
    safe_evacuation_corridors: Array.isArray(raw.safe_evacuation_corridors)
      ? raw.safe_evacuation_corridors.slice(0, 5).map((s) => String(s).slice(0, 120))
      : fallbackObj.safe_evacuation_corridors,
    impassable_infrastructure: Array.isArray(raw.impassable_infrastructure)
      ? raw.impassable_infrastructure.slice(0, 5).map((s) => String(s).slice(0, 120))
      : fallbackObj.impassable_infrastructure,
    nearest_open_hospital:
      raw.nearest_open_hospital && typeof raw.nearest_open_hospital === "object"
        ? {
            name: String(raw.nearest_open_hospital.name || fallbackObj.nearest_open_hospital.name).slice(0, 100),
            status: String(raw.nearest_open_hospital.status || "PASSABLE ON HIGH GROUND").slice(0, 60),
            distance_km: Number.isFinite(Number(raw.nearest_open_hospital.distance_km))
              ? Number(raw.nearest_open_hospital.distance_km)
              : fallbackObj.nearest_open_hospital.distance_km,
          }
        : fallbackObj.nearest_open_hospital,
    tactical_civic_advisory:
      typeof raw.tactical_civic_advisory === "string" && raw.tactical_civic_advisory.length > 5
        ? raw.tactical_civic_advisory.slice(0, 400)
        : fallbackObj.tactical_civic_advisory,
  };
}

export function buildDeterministicEdgeSop(telemetry, predictions, lat, lon) {
  const h1 = predictions.depth_trajectory_cm.h1;
  const h3 = predictions.depth_trajectory_cm.h3;
  const isCritical = h1 >= 15 || h3 >= 30 || telemetry.tideSurge >= 3.0;

  return {
    engine: "Tier-3 Deterministic Hydrological Edge SOP (Zero-API Guarantee)",
    verification_status: isCritical ? "VERIFIED_FLOOD_HAZARD" : "LOW_RISK_MONITORED",
    confidence_score: 91,
    causal_attribution:
      `Deterministic continuity check at (${lat.toFixed(3)}, ${lon.toFixed(3)}): ` +
      `${telemetry.r0.toFixed(1)} mm/hr rainfall over ${Math.round(telemetry.soilSat * 100)}% saturated soil ` +
      `with ${telemetry.tideSurge.toFixed(2)} m coastal surge projects +1h depth ${h1} cm and +3h depth ${h3} cm.`,
    danger_zone_perimeter: "Low-lying drainage sinks, rail underpasses, and basements within 500m radius.",
    safe_evacuation_corridors: [
      "Nearest elevated arterial flyover or viaduct (+8m above street datum)",
      "Primary ridge-line evacuation road outside storm-drainage depression",
    ],
    impassable_infrastructure: [
      "Submerged road/rail underpasses",
      "Ground-level basement parking and stormwater culverts",
    ],
    nearest_open_hospital: {
      name: "Nearest Municipal Emergency Trauma Facility (Verify local route elevation)",
      status: "CHECK_ELEVATED_ACCESS",
      distance_km: 1.5,
    },
    tactical_civic_advisory: isCritical
      ? "CRITICAL: Move immediately to higher ground or upper floors. Never drive or walk into moving floodwater."
      : "ADVISORY: Monitor local water levels and avoid low-lying underpasses as runoff accumulates.",
  };
}

export async function runTacticalReasoning(env, telemetry, predictions, lat, lon, options = {}) {
  const skipCache = Boolean(options.skipCache);
  const clusterKey =
    `ai_cache:${lat.toFixed(2)}_${lon.toFixed(2)}` +
    `_r0_${Math.round(telemetry.r0 / 5)}` +
    `_r48_${Math.round(telemetry.r48 / 20)}` +
    `_sat_${Math.round(telemetry.soilSat * 10)}` +
    `_tide_${Math.round(telemetry.tideSurge * 2)}`;

  if (!skipCache && env.FLOODLOCK_KV) {
    const cached = await env.FLOODLOCK_KV.get(clusterKey, "json");
    if (cached) return { ...cached, cache_hit: true };
  }

  const deterministicFloor = buildDeterministicEdgeSop(telemetry, predictions, lat, lon);
  const cbStub = env.CIRCUIT_BREAKER_DO
    ? env.CIRCUIT_BREAKER_DO.get(env.CIRCUIT_BREAKER_DO.idFromName("global-ai-cb"))
    : null;

  const prompt = `You are the Lead Hydrological Intelligence Officer for FloodLock.
Return ONLY a valid JSON object matching the exact schema below.

Coordinates: Lat ${lat}, Lon ${lon}
Meteorology: R0=${telemetry.r0} mm/hr, R48=${telemetry.r48} mm, R120=${telemetry.r120} mm, CAPE=${telemetry.cape} J/kg, SoilSat=${Math.round(telemetry.soilSat * 100)}%, TideSurge=${telemetry.tideSurge} m.
Neural Edge Forecast: +1h=${predictions.depth_trajectory_cm.h1}cm, +3h=${predictions.depth_trajectory_cm.h3}cm, +6h=${predictions.depth_trajectory_cm.h6}cm, Q=${predictions.runoff_q_m3s} m3/s, Prob=${predictions.flash_flood_probability}.

REQUIRED JSON SCHEMA:
{
  "verification_status": "VERIFIED_FLOOD_HAZARD" or "FALSE_ALARM_DOWNGRADED",
  "confidence_score": 1-100,
  "causal_attribution": "1-2 concise physical sentences",
  "danger_zone_perimeter": "Low-lying basin description",
  "safe_evacuation_corridors": ["Specific elevated road or flyover"],
  "impassable_infrastructure": ["Specific underpass or tunnel"],
  "nearest_open_hospital": {"name": "Hospital", "status": "PASSABLE ON HIGH GROUND", "distance_km": 1.2},
  "tactical_civic_advisory": "1-2 actionable safety sentences"
}`;

  const groqModel = env.GROQ_MODEL || "openai/gpt-oss-120b";
  if (env.GROQ_API_KEY) {
    const groqTripped = cbStub ? await cbStub.isOpen("groq") : false;
    if (!groqTripped) {
      try {
        const qRes = await fetchWithTimeout(
          "https://api.groq.com/openai/v1/chat/completions",
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${env.GROQ_API_KEY}`,
              "Content-Type": "application/json",
              "User-Agent": "MeteoFlood/3.2",
            },
            body: JSON.stringify({
              model: groqModel,
              messages: [{ role: "user", content: prompt }],
              response_format: { type: "json_object" },
              temperature: 0.1,
              max_tokens: 800,
            }),
          },
          3500
        );
        if (qRes.ok) {
          const qData = await qRes.json();
          const parsed = JSON.parse(qData.choices[0].message.content);
          const normalized = normalizeTacticalPayload(parsed, `Tier-1 Groq LPU (${groqModel})`, deterministicFloor);
          if (cbStub) await cbStub.recordSuccess("groq");
          if (!skipCache && env.FLOODLOCK_KV) {
            await env.FLOODLOCK_KV.put(clusterKey, JSON.stringify(normalized), { expirationTtl: 600 });
          }
          return normalized;
        }
        if (cbStub) await cbStub.recordFailure("groq");
      } catch {
        if (cbStub) await cbStub.recordFailure("groq");
      }
    }
  }

  const geminiModel = env.GEMINI_MODEL || "gemini-2.5-flash";
  if (env.GEMINI_API_KEY) {
    const geminiTripped = cbStub ? await cbStub.isOpen("gemini") : false;
    if (!geminiTripped) {
      try {
        const gRes = await fetchWithTimeout(
          `https://generativelanguage.googleapis.com/v1beta/models/${geminiModel}:generateContent`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "x-goog-api-key": env.GEMINI_API_KEY,
            },
            body: JSON.stringify({
              contents: [{ parts: [{ text: prompt }] }],
              generationConfig: {
                temperature: 0.1,
                responseMimeType: "application/json",
                maxOutputTokens: 800,
                thinkingConfig: { thinkingLevel: "low" },
              },
            }),
          },
          3500
        );
        if (gRes.ok) {
          const gData = await gRes.json();
          const rawText = gData.candidates?.[0]?.content?.parts?.[0]?.text;
          const parsed = JSON.parse(rawText);
          const normalized = normalizeTacticalPayload(parsed, `Tier-2 Google Cloud (${geminiModel} GA)`, deterministicFloor);
          if (cbStub) await cbStub.recordSuccess("gemini");
          if (!skipCache && env.FLOODLOCK_KV) {
            await env.FLOODLOCK_KV.put(clusterKey, JSON.stringify(normalized), { expirationTtl: 600 });
          }
          return normalized;
        }
        if (cbStub) await cbStub.recordFailure("gemini");
      } catch {
        if (cbStub) await cbStub.recordFailure("gemini");
      }
    }
  }

  return deterministicFloor;
}
