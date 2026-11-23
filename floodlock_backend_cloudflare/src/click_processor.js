/**
 * cloudflare_worker/src/click_processor.js
 * ============================================================================
 * FloodLock v3.2 Gold — Dedicated Interactive User Click & Point Forecast Core
 * Core Role: DEDICATED_USER_CLICK_PROCESSOR (Worker Core #3)
 *
 * Exclusively handles interactive user clicks, pinpoint coordinate queries,
 * and high-priority on-demand forecast requests:
 *  - Sub-300ms interactive response time isolated from planetary mesh jobs
 *  - 14-Feature Neural Forward Pass (predict14F)
 *  - Adversarial Groq LPU Verification Gate (openai/gpt-oss-120b)
 *  - Threat Suppression: if Groq flags false alarm, suppresses alarm completely
 *  - Structured Flood Audit Telemetry logged and returned
 * ============================================================================
 */

import { WEIGHTS_14F } from "./weights_14f.js";
import { runTacticalReasoning } from "./ai_resilience.js";

const DEFAULT_ORIGINS = [
  "https://metoflood.netlify.app",
  "https://floodlock.pages.dev",
  "https://floodnet.netlify.app",
  "https://dakshdahore1995-design.github.io",
  "http://localhost:3000",
  "http://127.0.0.1:3000",
  "http://localhost:8000",
  "http://127.0.0.1:8000"
];

const KNOWN_BASINS = [
  { name: "Mithi-Ulhas River Basin (Mumbai)", lat: 19.076, lon: 72.877, water_prox: 0.95, ks_mm_hr: 4.5, twi: 0.88, impervious: 0.82 },
  { name: "Danube River Basin (Budapest)", lat: 47.497, lon: 19.040, water_prox: 0.85, ks_mm_hr: 18.0, twi: 0.65, impervious: 0.55 },
  { name: "Rhine-Meuse Basin (Cologne)", lat: 50.937, lon: 6.960, water_prox: 0.80, ks_mm_hr: 22.0, twi: 0.60, impervious: 0.60 },
  { name: "Ganges River Basin (Varanasi)", lat: 25.317, lon: 82.973, water_prox: 0.90, ks_mm_hr: 12.0, twi: 0.78, impervious: 0.65 },
  { name: "Mississippi River Basin (New Orleans)", lat: 29.951, lon: -90.071, water_prox: 0.92, ks_mm_hr: 8.0, twi: 0.85, impervious: 0.70 },
  { name: "Amazon River Basin (Manaus)", lat: -3.119, lon: -60.021, water_prox: 0.98, ks_mm_hr: 25.0, twi: 0.92, impervious: 0.25 },
  { name: "Nile River Basin (Cairo)", lat: 30.044, lon: 31.235, water_prox: 0.75, ks_mm_hr: 15.0, twi: 0.50, impervious: 0.75 },
  { name: "Thames River Basin (London)", lat: 51.507, lon: -0.127, water_prox: 0.82, ks_mm_hr: 16.0, twi: 0.62, impervious: 0.78 },
  { name: "Seine River Basin (Paris)", lat: 48.856, lon: 2.352, water_prox: 0.78, ks_mm_hr: 19.0, twi: 0.58, impervious: 0.74 },
  { name: "Yangtze River Basin (Wuhan)", lat: 30.592, lon: 114.305, water_prox: 0.88, ks_mm_hr: 10.0, twi: 0.82, impervious: 0.72 }
];

function findNearestBasin(lat, lon) {
  let closest = KNOWN_BASINS[0];
  let minDistanceSq = Infinity;
  for (const b of KNOWN_BASINS) {
    const dLat = b.lat - lat;
    const dLon = b.lon - lon;
    const distSq = dLat * dLat + dLon * dLon;
    if (distSq < minDistanceSq) {
      minDistanceSq = distSq;
      closest = b;
    }
  }
  const isClose = Math.sqrt(minDistanceSq) < 2.5; // Within ~250km
  return {
    basin_id: isClose ? closest.name : "Custom Terrestrial Catchment",
    name: isClose ? closest.name : `Terrestrial Quad (${lat.toFixed(2)}°, ${lon.toFixed(2)}°)`,
    water_prox: isClose ? closest.water_prox : 0.40,
    ks_mm_hr: isClose ? closest.ks_mm_hr : 20.0,
    twi: isClose ? closest.twi : 0.55,
    impervious: isClose ? closest.impervious : 0.45
  };
}

function predict14F(features) {
  const t0 = performance.now();
  const { W1, b1, W2, b2, W3, b3 } = WEIGHTS_14F;

  const h1 = new Float32Array(32);
  for (let i = 0; i < 32; i++) {
    let s = b1[i];
    for (let j = 0; j < 14; j++) s += W1[i][j] * features[j];
    h1[i] = Math.max(0.0, s);
  }

  const h2 = new Float32Array(16);
  for (let i = 0; i < 16; i++) {
    let s = b2[i];
    for (let j = 0; j < 32; j++) s += W2[i][j] * h1[j];
    h2[i] = Math.max(0.0, s);
  }

  const out = new Float32Array(6);
  for (let i = 0; i < 6; i++) {
    let s = b3[i];
    for (let j = 0; j < 16; j++) s += W3[i][j] * h2[j];
    out[i] = s;
  }

  const h1_depth = Math.max(0.0, Math.min(500.0, Math.round(out[0] * 10) / 10));
  const h3_depth = Math.max(0.0, Math.min(500.0, Math.round(out[1] * 10) / 10));
  const h6_depth = Math.max(0.0, Math.min(500.0, Math.round(out[2] * 10) / 10));
  const runoff_q = Math.max(0.0, Math.round(out[3] * 100) / 100);
  const logitP = Math.max(-20.0, Math.min(20.0, out[4]));
  const logitU = Math.max(-20.0, Math.min(20.0, out[5]));
  const flood_prob = Math.round((1.0 / (1.0 + Math.exp(-logitP))) * 1000) / 1000;
  const urgency = Math.round((1.0 / (1.0 + Math.exp(-logitU))) * 1000) / 1000;

  return {
    depth_trajectory_cm: { h1: h1_depth, h3: h3_depth, h6: h6_depth },
    runoff_q_m3s: runoff_q,
    flash_flood_probability: flood_prob,
    urgency_index: urgency,
    latency_ms: Math.round((performance.now() - t0) * 1000) / 1000,
    model_version: "GlobalHydrology-14F-v3.2-ClickProcessor",
  };
}

const TELEMETRY_CACHE = new Map();

async function fetchLiveTelemetryWithCache(lat, lon) {
  const cacheKey = `${lat.toFixed(2)}_${lon.toFixed(2)}`;
  const now = Date.now();
  if (TELEMETRY_CACHE.has(cacheKey)) {
    const entry = TELEMETRY_CACHE.get(cacheKey);
    if (now - entry.timestamp < 180000) { // 3-minute in-worker cache
      return entry.data;
    }
  }

  const weatherUrl =
    `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}` +
    `&current=precipitation,rain,surface_pressure,wind_speed_10m,wind_direction_10m,cape` +
    `&hourly=precipitation,soil_moisture_0_to_100cm&past_days=5`;
  const marineUrl =
    `https://marine-api.open-meteo.com/v1/marine?latitude=${lat}&longitude=${lon}` +
    `&hourly=wave_height,ocean_current_velocity`;

  let weatherData = null;
  let marineData = null;
  try {
    const [wRes, mRes] = await Promise.all([
      fetch(weatherUrl, { headers: { "User-Agent": "FloodLock-ClickProcessor/3.2" }, signal: AbortSignal.timeout(3500) }),
      fetch(marineUrl, { headers: { "User-Agent": "FloodLock-ClickProcessor/3.2" }, signal: AbortSignal.timeout(3500) }).catch(() => null),
    ]);
    if (wRes && wRes.ok) weatherData = await wRes.json();
    if (mRes && mRes.ok) marineData = await mRes.json();
  } catch {}

  const current = weatherData?.current || {};
  const hourly = weatherData?.hourly || {};
  const r0 = Math.max(0.0, Number(current.precipitation ?? current.rain ?? 0.0));
  const cape = Math.max(0.0, Number(current.cape ?? 500.0));
  const pressure = Number(current.surface_pressure ?? 1013.25);
  const wind = Math.max(0.0, Number(current.wind_speed_10m ?? 15.0));

  const pastRain = Array.isArray(hourly.precipitation) ? hourly.precipitation : [];
  const r48 = pastRain.length ? pastRain.slice(-48).reduce((a, b) => a + Math.max(0, Number(b || 0)), 0) : r0 * 4.5;
  const r120 = pastRain.length ? pastRain.slice(-120).reduce((a, b) => a + Math.max(0, Number(b || 0)), 0) : r0 * 12.0;

  const soilArr = Array.isArray(hourly.soil_moisture_0_to_100cm) ? hourly.soil_moisture_0_to_100cm : [];
  const soilSat = soilArr.length ? Number(soilArr[soilArr.length - 1] ?? 0.45) : 0.45;
  const waves = Array.isArray(marineData?.hourly?.wave_height) ? marineData.hourly.wave_height : [];
  const tideSurge = waves.length ? Math.max(0.0, Number(waves[waves.length - 1] ?? 0.0)) : 0.0;

  const result = {
    r0,
    r48: Math.round(r48 * 10) / 10,
    r120: Math.round(r120 * 10) / 10,
    cape,
    dp: Math.round((pressure - 1013.25) * 10) / 10,
    wind,
    soilSat: Math.min(1.0, Math.max(0.0, soilSat)),
    tideSurge: Math.min(6.0, tideSurge),
  };

  TELEMETRY_CACHE.set(cacheKey, { timestamp: now, data: result });
  if (TELEMETRY_CACHE.size > 500) {
    const oldestKey = TELEMETRY_CACHE.keys().next().value;
    TELEMETRY_CACHE.delete(oldestKey);
  }

  return result;
}

function getCorsHeaders(request, env) {
  const origin = request.headers.get("Origin") || "";
  const allowed = (env.ALLOWED_ORIGINS || DEFAULT_ORIGINS.join(",")).split(",").map(s => s.trim());
  const match = allowed.includes(origin) ? origin : allowed[0];
  return {
    "Access-Control-Allow-Origin": match,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, X-Session-Token",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function jsonResponse(request, env, data, status = 200, extraHeaders = {}) {
  const cors = getCorsHeaders(request, env);
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...cors,
      ...extraHeaders,
    },
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const method = request.method;
    const path = url.pathname;

    if (method === "OPTIONS") {
      return new Response(null, { status: 204, headers: getCorsHeaders(request, env) });
    }

    // Health & Core Identity
    if (path === "/health" || path === "/status" || path === "/") {
      return jsonResponse(request, env, {
        status: "ONLINE",
        worker: "floodlock-click-processor",
        core_index: 3,
        role: "DEDICATED_USER_CLICK_PROCESSOR",
        cluster_assignment: "Interactive User Clicks & Point Queries",
        cache_entries: TELEMETRY_CACHE.size,
        timestamp: new Date().toISOString(),
      });
    }

    // Interactive Point Query / Click Processor
    if (path === "/api/forecast" || path === "/api/click-point" || path === "/api/user-click") {
      let lat, lon;
      if (method === "POST") {
        try {
          const body = await request.json();
          lat = parseFloat(body.lat ?? body.latitude);
          lon = parseFloat(body.lon ?? body.longitude);
        } catch {
          return jsonResponse(request, env, { error: "INVALID_JSON_BODY" }, 400);
        }
      } else {
        lat = parseFloat(url.searchParams.get("lat") || url.searchParams.get("latitude"));
        lon = parseFloat(url.searchParams.get("lon") || url.searchParams.get("longitude"));
      }

      if (!Number.isFinite(lat) || !Number.isFinite(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
        return jsonResponse(request, env, { error: "INVALID_COORDINATES", message: "lat [-90,90], lon [-180,180] required" }, 400);
      }

      const basin = findNearestBasin(lat, lon);
      let telem = await fetchLiveTelemetryWithCache(lat, lon);

      const scenario = (url.searchParams.get("scenario") || "").toLowerCase();
      const hasR0 = url.searchParams.has("r0");
      const hasR48 = url.searchParams.has("r48");
      const hasSoil = url.searchParams.has("soil_sat") || url.searchParams.has("soilSat");
      const hasTide = url.searchParams.has("tide") || url.searchParams.has("tideSurge");
      const forceThreat = url.searchParams.get("force_threat") === "true";

      if (scenario.includes("mumbai") || scenario.includes("monsoon") || scenario.includes("extreme")) {
        telem = {
          ...telem,
          r0: 68.0,
          r48: 240.0,
          r120: 380.0,
          soilSat: 0.95,
          tideSurge: 2.8,
          cape: 2400.0,
        };
      } else if (scenario.includes("dry") || scenario.includes("false_alarm") || scenario.includes("benign")) {
        telem = {
          ...telem,
          r0: 0.2,
          r48: 1.0,
          r120: 3.0,
          soilSat: 0.12,
          tideSurge: 0.0,
          cape: 150.0,
        };
      } else if (hasR0 || hasR48 || hasSoil || hasTide) {
        telem = {
          ...telem,
          r0: hasR0 ? parseFloat(url.searchParams.get("r0")) : telem.r0,
          r48: hasR48 ? parseFloat(url.searchParams.get("r48")) : telem.r48,
          soilSat: hasSoil ? parseFloat(url.searchParams.get("soil_sat") || url.searchParams.get("soilSat")) : telem.soilSat,
          tideSurge: hasTide ? parseFloat(url.searchParams.get("tide") || url.searchParams.get("tideSurge")) : telem.tideSurge,
        };
      }

      const spi30Est = Math.min(3.0, Math.max(-3.0, telem.r48 / 80.0 - 0.5));
      const spi90Est = Math.min(3.0, Math.max(-3.0, telem.r120 / 160.0 - 0.5));

      const features = [
        Math.min(1.0, telem.r0 / 250.0),
        Math.min(1.0, telem.r48 / 500.0),
        Math.min(1.0, telem.r120 / 1000.0),
        Math.min(1.0, telem.cape / 4500.0),
        Math.min(1.0, Math.max(0.0, (telem.dp + 15.0) / 20.0)),
        Math.min(1.0, telem.wind / 180.0),
        Math.min(1.0, Math.max(0.0, (spi30Est + 3.0) / 6.0)),
        Math.min(1.0, Math.max(0.0, (spi90Est + 3.0) / 6.0)),
        telem.soilSat,
        Math.min(1.0, basin.ks_mm_hr / 50.0),
        basin.water_prox,
        basin.twi,
        basin.impervious,
        Math.min(1.0, telem.tideSurge / 6.0),
      ];

      const neuralPred = predict14F(features);
      const isBlackSwan = telem.r0 > 50.0 && features[12] > 0.70;
      const isThreat =
        forceThreat ||
        isBlackSwan ||
        neuralPred.depth_trajectory_cm.h1 > 8.0 ||
        neuralPred.flash_flood_probability > 0.40 ||
        (telem.r0 > 15.0 && telem.soilSat > 0.75);

      let tacticalReasoning = null;
      if (isThreat) {
        tacticalReasoning = await runTacticalReasoning(env, telem, neuralPred, lat, lon, {
          skipCache: false,
        });
      }

      // Adversarial Groq Verification Gate
      const groqVerified = tacticalReasoning && (tacticalReasoning.threat_verified === true || tacticalReasoning.verification_status === "VERIFIED_FLOOD_HAZARD");
      const groqDismissed = tacticalReasoning && (tacticalReasoning.threat_verified === false || tacticalReasoning.verification_status === "FALSE_ALARM_DOWNGRADED");

      let finalThreatLevel = "MONITORED_NOMINAL";
      if (isThreat) {
        if (groqDismissed) {
          finalThreatLevel = "NOMINAL";
        } else if (groqVerified || !tacticalReasoning) {
          finalThreatLevel = "CRITICAL_INUNDATION";
        }
      }

      // Structured Flood Audit Telemetry
      const floodAuditLog = {
        timestamp: new Date().toISOString(),
        target_coordinates: { lat, lon },
        hydrology: {
          nearest_basin: basin.name,
          water_proximity_m: Math.round(basin.water_prox * 1000),
          soil_ks_mm_hr: basin.ks_mm_hr,
          topographic_wetness_index: basin.twi,
          impervious_surface_fraction: basin.impervious,
        },
        live_meteorology: {
          rain_rate_r0_mm_hr: telem.r0,
          accum_48h_mm: telem.r48,
          accum_120h_mm: telem.r120,
          soil_saturation_pct: Math.round(telem.soilSat * 100),
          coastal_tide_surge_m: telem.tideSurge,
          convective_cape_j_kg: telem.cape,
        },
        neural_forward_pass: {
          depth_trajectory_cm: neuralPred.depth_trajectory_cm,
          runoff_q_m3s: neuralPred.runoff_q_m3s,
          flash_flood_probability: neuralPred.flash_flood_probability,
          raw_neural_threat_flag: isThreat,
        },
        adversarial_groq_audit: {
          groq_called: Boolean(isThreat),
          engine: tacticalReasoning ? tacticalReasoning.engine : "None (Sub-threshold)",
          groq_verdict: groqDismissed ? "FALSE_ALARM_DOWNGRADED" : (groqVerified ? "CONFIRMED_FLOOD_HAZARD" : "NOMINAL_MONITORED"),
          threat_verified: groqVerified,
          confidence_score: tacticalReasoning ? tacticalReasoning.confidence_score : 99,
          physical_audit_summary: tacticalReasoning ? (tacticalReasoning.physical_consistency_audit || tacticalReasoning.causal_attribution) : "Nominal hydrological equilibrium.",
          action_taken: groqDismissed ? "ALARM_SUPPRESSED_FALSE_ALARM" : (groqVerified ? "CRITICAL_ALARM_DISPATCHED" : "ROUTINE_MONITORING"),
        }
      };

      console.log(`[CLICK_PROCESSOR_AUDIT] Lat:${lat.toFixed(3)}, Lon:${lon.toFixed(3)} | NeuralDepth:+1h=${neuralPred.depth_trajectory_cm.h1}cm | GroqVerdict:${floodAuditLog.adversarial_groq_audit.groq_verdict} | Action:${floodAuditLog.adversarial_groq_audit.action_taken}`);

      return jsonResponse(request, env, {
        timestamp: new Date().toISOString(),
        processor_core: "floodlock-click-processor",
        coordinates: { lat, lon },
        telemetry: telem,
        basin_parameters: basin,
        neural_predictions: neuralPred,
        threat_level: finalThreatLevel,
        groq_audit_verdict: floodAuditLog.adversarial_groq_audit.groq_verdict,
        flood_audit_log: floodAuditLog,
        dual_trigger_black_swan: isBlackSwan,
        tactical_reasoning: groqDismissed ? null : tacticalReasoning,
      }, 200, {
        "X-Worker-Core": "Core-3-ClickProcessor",
        "X-Response-Time-Ms": `${neuralPred.latency_ms}`,
      });
    }

    return jsonResponse(request, env, { error: "NOT_FOUND" }, 404);
  }
};
