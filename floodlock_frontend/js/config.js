/**
 * floodlock_frontend/js/config.js
 * ────────────────────────────────────────────────────────────────────────────
 * Central configuration, multi-tier backend failover, and hardware node discovery.
 * 
 * SECURITY MANDATE:
 * API keys (OpenWeather, Tomorrow.io, WorldTides) are strictly kept on the
 * backend server (.env) and NEVER exposed in frontend code.
 */

const DEFAULT_CONFIG = {
  // 24/7 Permanent Cloudflare Edge Backend (Zero Local PC Compute, Qwen AI & Dual MLP)
  CLOUDFLARE_EDGE_URL: "https://floodlock-backend.dakshdahore1995.workers.dev",

  // Public HTTPS Cloudflare Tunnel directly to Windows Laptop (YuvaMPS1 @ 192.168.1.106)
  PUBLIC_TUNNEL_URL: "https://subscribers-sustained-cannon-moderator.trycloudflare.com",
  
  // Local network fallback (if accessed on the same Wi-Fi)
  LOCAL_BACKEND_URL: "http://192.168.1.106:8000",

  // Cloud secondary fallback (Render / Fly.io)
  CLOUD_BACKEND_URL: "https://floodlock-backend-cloud.onrender.com",

  ACTIVE_THEME: "dark"
};

class ConfigManager {
  constructor() {
    this.config = { ...DEFAULT_CONFIG };
    this.loadFromStorage();
    this.activeBackend = "TUNNEL"; // "TUNNEL" | "LOCAL" | "CLOUD" | "EDGE"
    this.isOnline = true;
    this.telemetryCache = null;
  }

  loadFromStorage() {
    for (const key of Object.keys(DEFAULT_CONFIG)) {
      const stored = localStorage.getItem(`FLOODLOCK_${key}`);
      if (stored !== null && stored !== "") {
        this.config[key] = stored;
      }
    }
  }

  saveKey(key, value) {
    this.config[key] = value;
    localStorage.setItem(`FLOODLOCK_${key}`, value);
  }

  get(key) {
    return this.config[key] || DEFAULT_CONFIG[key] || "";
  }

  async detectBestBackend() {
    // Helper for strict timed fetch (1500ms timeout, silent catch)
    const timedFetch = async (url, timeoutMs = 1500) => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        const res = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        return res;
      } catch (e) {
        return null;
      }
    };

    // 1. Try 24/7 Permanent Cloudflare Edge Backend First (5000ms — generous for cold starts)
    const cfUrl = this.get("CLOUDFLARE_EDGE_URL") || "https://floodlock-backend.dakshdahore1995.workers.dev";
    if (cfUrl) {
      const res = await timedFetch(`${cfUrl}/health`, 5000);
      if (res && res.ok) {
        try {
          const data = await res.json();
          this.activeBackend = "CLOUDFLARE";
          this.telemetryCache = data;
          return {
            tier: "CLOUDFLARE",
            url: cfUrl,
            name: "CLOUDFLARE 24/7 EDGE [QWEN & DUAL MLP]",
            data: data
          };
        } catch (e) {
          // JSON parse issue, fall through
        }
      }
    }

    // 2. Try Public HTTPS Tunnel (1500ms timeout)
    const tunnelUrl = this.get("PUBLIC_TUNNEL_URL");
    if (tunnelUrl) {
      const res = await timedFetch(`${tunnelUrl}/health`, 1500);
      if (res && res.ok) {
        try {
          const data = await res.json();
          this.activeBackend = "TUNNEL";
          this.telemetryCache = data;
          return {
            tier: "TUNNEL",
            url: tunnelUrl,
            name: "MSI LAPTOP SENTINEL [TUNNEL LIVE]",
            data: data
          };
        } catch (e) {
          // JSON parse issue, fall through
        }
      }
    }

    // 2. Try Direct Local / LAN Backend (only if HTTP to avoid mixed content block, 800ms timeout)
    const localCandidates = [
      "http://127.0.0.1:8000",
      "http://localhost:8000",
      this.get("LOCAL_BACKEND_URL"),
      "http://192.168.1.106:8000"
    ];
    for (const localUrl of localCandidates) {
      if (localUrl && window.location.protocol === "http:") {
        const res = await timedFetch(`${localUrl}/health`, 800);
        if (res && res.ok) {
          try {
            const data = await res.json();
            this.activeBackend = "LOCAL";
            this.telemetryCache = data;
            return {
              tier: "LOCAL",
              url: localUrl,
              name: "LOCAL BACKEND [LIVE :8000]",
              data: data
            };
          } catch (e) {
            // Next candidate
          }
        }
      }
    }

    // 3. Try Cloud Serverless API (Hosted directly on Netlify / same origin, 1500ms timeout)
    const currentOrigin = (typeof window !== "undefined" && window.location && window.location.origin) ? window.location.origin : "";
    if (currentOrigin && !currentOrigin.includes("127.0.0.1") && !currentOrigin.includes("localhost") && !currentOrigin.includes("192.168.")) {
      const res = await timedFetch(`${currentOrigin}/api/health`, 1500);
      if (res && res.ok) {
        try {
          const data = await res.json();
          this.activeBackend = "CLOUD";
          this.telemetryCache = data;
          return {
            tier: "CLOUD",
            url: currentOrigin,
            name: "CLOUD NETLIFY [SERVERLESS]",
            data: data
          };
        } catch (e) {
          // Next candidate
        }
      }
    }

    // 4. Try External Cloud Fallback URL (1500ms timeout)
    const cloudUrl = this.get("CLOUD_BACKEND_URL");
    if (cloudUrl) {
      const res = await timedFetch(`${cloudUrl}/health`, 1500);
      if (res && res.ok) {
        try {
          const data = await res.json();
          this.activeBackend = "CLOUD";
          this.telemetryCache = data;
          return {
            tier: "CLOUD",
            url: cloudUrl,
            name: "CLOUD BACKEND [ONLINE]",
            data: data
          };
        } catch (e) {
          // Next candidate
        }
      }
    }

    // 5. Pure In-Browser Edge MLP (Zero-Latency Local Physics & Neural Net)
    this.activeBackend = "EDGE";
    return {
      tier: "EDGE",
      url: null,
      name: "[OFFLINE DEMO MODE: Edge MLP Active]",
      data: null
    };
  }
}

window.FloodConfig = new ConfigManager();
