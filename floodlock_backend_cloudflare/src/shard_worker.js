/**
 * floodlock_backend_cloudflare/src/shard_worker.js
 * ═══════════════════════════════════════════════════════════════════════════
 * MeteoFlood Continental AMR Compute Shard Worker
 * Dedicated Cloudflare V8 Edge Isolate for Regional Shard Processing.
 * ═══════════════════════════════════════════════════════════════════════════
 */

import { generateShardAMRHeatGrid } from "./planetary_grid.js";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const region = env.SHARD_REGION || url.searchParams.get("region") || "Asia";
    const path = url.pathname;

    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    if (path === "/health" || path === "/") {
      return new Response(JSON.stringify({
        service: "MeteoFlood Continental AMR Compute Shard",
        status: "ONLINE",
        shard_name: env.SHARD_NAME || `floodlock-shard-${region.toLowerCase()}`,
        region,
        datacenter: request.cf?.colo || "EDGE",
        timestamp: new Date().toISOString()
      }), {
        headers: { "Content-Type": "application/json", ...corsHeaders }
      });
    }

    if (path === "/api/mesh/shard") {
      const t0 = performance.now();
      const shardData = await generateShardAMRHeatGrid(region);
      const duration = Math.round((performance.now() - t0) * 10) / 10;

      return new Response(JSON.stringify({
        shard: env.SHARD_NAME || `floodlock-shard-${region.toLowerCase()}`,
        region,
        datacenter: request.cf?.colo || "EDGE",
        compute_time_ms: duration,
        ...shardData
      }), {
        headers: {
          "Content-Type": "application/json",
          "X-Shard-Region": region,
          "X-Shard-Compute-Ms": String(duration),
          ...corsHeaders
        }
      });
    }

    return new Response(JSON.stringify({ error: "NOT_FOUND", path }), { status: 404, headers: corsHeaders });
  }
};

