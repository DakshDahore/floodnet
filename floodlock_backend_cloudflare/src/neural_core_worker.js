/**
 * floodlock_backend_cloudflare/src/neural_core_worker.js
 * ═══════════════════════════════════════════════════════════════════════════
 * MeteoFlood Planetary Neural Core Isolate (Core 3 of 10)
 * Dedicated V8 Compute Isolate for 14-Feature Deep Hydrology Inference
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { predict14F } from "./planetary_grid.js";
import { WEIGHTS_14F } from "./weights_14f.js";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (path === "/health" || path === "/" || path === "/api/neural/status") {
      return new Response(JSON.stringify({
        service: "MeteoFlood Planetary Neural Core (14F Tensor Isolate)",
        status: "ONLINE",
        core_index: 3,
        total_cores: 10,
        model_version: "GlobalHydrology-14F-v3.2-Gold",
        weights_architecture: "14-Input -> 32-ReLU -> 16-ReLU -> 6-Head Multi-Objective Out",
        datacenter: request.cf?.colo || "EDGE",
        timestamp: new Date().toISOString()
      }), {
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }

    if (path === "/api/neural/predict" && request.method === "POST") {
      try {
        const body = await request.json();
        if (body.batch && Array.isArray(body.batch)) {
          const t0 = performance.now();
          const results = body.batch.map(feats => predict14F(feats));
          const duration = Math.round((performance.now() - t0) * 100) / 100;
          return new Response(JSON.stringify({
            batch_size: results.length,
            batch_latency_ms: duration,
            predictions: results
          }), {
            headers: { "Content-Type": "application/json", ...corsHeaders }
          });
        }

        const feats = body.features;
        if (!Array.isArray(feats) || feats.length !== 14) {
          return new Response(JSON.stringify({
            error: "INVALID_FEATURE_VECTOR",
            message: "Expected 14 normalized float features."
          }), { status: 400, headers: { "Content-Type": "application/json", ...corsHeaders } });
        }

        const pred = predict14F(feats);
        return new Response(JSON.stringify(pred), {
          headers: { "Content-Type": "application/json", ...corsHeaders }
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: "NEURAL_INFERENCE_ERROR", message: err.message }), {
          status: 500,
          headers: { "Content-Type": "application/json", ...corsHeaders }
        });
      }
    }

    return new Response(JSON.stringify({ error: "NOT_FOUND", path }), { status: 404, headers: corsHeaders });
  }
};

