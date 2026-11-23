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
  // Primary 24/7 Cloudflare Edge Backend (Worker Slot A / Active)
  CLOUDFLARE_EDGE_URL: "https://floodlock-backend.dakshdahore1995.workers.dev",

  // Hot Standby Cloudflare Edge Backend (Worker Slot B / Redundant Pair for Zero Downtime)
  CLOUDFLARE_STANDBY_URL: "https://floodlock-backend-standby.dakshdahore1995.workers.dev",

  // Public HTTPS Cloudflare Tunnel directly to Windows Laptop (YuvaMPS1 @ 192.168.1.106)
  PUBLIC_TUNNEL_URL: "https://subscribers-sustained-cannon-moderator.trycloudflare.com",
  
  // Local network fallback (if accessed on the same Wi-Fi)
  LOCAL_BACKEND_URL: "http://192.168.1.106:8000",

  // Cloud secondary fallback (Render / Fly.io)
  CLOUD_BACKEND_URL: "https://floodlock-backend-cloud.onrender.com",

  ACTIVE_THEME: "dark"
};

/**
 * FloodLock v3.2 Production API Routes
 */
const FLOODLOCK_ENDPOINTS = {
  HEALTH: "/health",
  ROOT: "/",
  FORECAST: "/api/forecast",
  LIVE_MUMBAI: "/api/live-mumbai",
  FLOOD_PLANETARY_HEATGRID: "/api/flood/planetary-heatgrid",
  FLOOD_ACTIVE: "/api/flood/active",
  FLOOD_TELEMETRY: "/api/flood/telemetry",
  FLOOD_RADIUS_CHECK: "/api/flood/radius-check",
  STATE_CACHE: "/api/state-cache",
  AUTH_SEND_OTP: "/api/auth/send-otp",
  AUTH_VERIFY_OTP: "/api/auth/verify-otp",
  AUTH_OAUTH_GOOGLE: "/api/auth/oauth/google",
  AUTH_OAUTH_GITHUB: "/api/auth/oauth/github",
  AUTH_OAUTH_EXCHANGE: "/api/auth/oauth/exchange",
  USER_PROFILE: "/api/user/profile",
  BILLING_WEBHOOK: "/api/billing/webhook",
  BILLING_REFUND: "/api/billing/refund",
  INQUIRY: "/api/inquiry",
  CONTRIBUTE: "/api/contribute",
  ADMIN_INQUIRIES: "/api/admin/inquiries",
  ADMIN_USERS: "/api/admin/users",
  ADMIN_APPROVE: "/api/admin/approve-inquiry",
  ADMIN_DISMISS: "/api/admin/dismiss-inquiry",
  ADMIN_REVOKE: "/api/admin/revoke-user",
  ADMIN_PROVISION: "/api/admin/provision-user",
  ADMIN_SEND_EMAIL: "/api/admin/send-email",
};

class ConfigManager {
  constructor() {
    this.config = { ...DEFAULT_CONFIG };
    this.loadFromStorage();
    this.activeBackend = "CLOUDFLARE"; // Default to 24/7 Edge
    this.isOnline = true;
    this.telemetryCache = null;
    this.endpoints = FLOODLOCK_ENDPOINTS;
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

  // ── Authentication & Token Session Helpers ──
  getSessionToken() {
    return localStorage.getItem("floodlock_session_token") || "";
  }

  setSession(token, user = null) {
    if (token) {
      localStorage.setItem("floodlock_session_token", token);
    }
    if (user) {
      localStorage.setItem("floodlock_user_profile", JSON.stringify(user));
    }
  }

  getUserProfile() {
    try {
      const raw = localStorage.getItem("floodlock_user_profile");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  clearSession() {
    localStorage.removeItem("floodlock_session_token");
    localStorage.removeItem("floodlock_user_profile");
  }

  getBaseUrl() {
    if (this.activeBackend === "CLOUDFLARE" || !this.activeBackend || this.activeBackend === "EDGE") {
      return this.get("CLOUDFLARE_EDGE_URL") || DEFAULT_CONFIG.CLOUDFLARE_EDGE_URL;
    }
    if (this.activeBackend === "TUNNEL") {
      return this.get("PUBLIC_TUNNEL_URL") || DEFAULT_CONFIG.CLOUDFLARE_EDGE_URL;
    }
    if (this.activeBackend === "LOCAL") {
      return this.get("LOCAL_BACKEND_URL") || DEFAULT_CONFIG.CLOUDFLARE_EDGE_URL;
    }
    if (this.activeBackend === "CLOUD") {
      return this.get("CLOUD_BACKEND_URL") || DEFAULT_CONFIG.CLOUDFLARE_EDGE_URL;
    }
    return DEFAULT_CONFIG.CLOUDFLARE_EDGE_URL;
  }

  getEndpointUrl(endpointKey, queryParams = null) {
    const base = this.getBaseUrl().replace(/\/+$/, "");
    let path = this.endpoints[endpointKey] || endpointKey;
    if (queryParams && typeof queryParams === "object") {
      const qs = new URLSearchParams(queryParams).toString();
      if (qs) path += (path.includes("?") ? "&" : "?") + qs;
    }
    return `${base}${path}`;
  }

  /**
   * Universal fetch helper with automatic Bearer token injection and timeout
   */
  /**
   * Universal fetch helper with automatic 2-Worker Active/Standby failover, Bearer token injection, and timeout
   */
  async fetchApi(endpointKey, options = {}) {
    const primaryBase = this.getBaseUrl().replace(/\/+$/, "");
    const standbyBase = (this.get("CLOUDFLARE_STANDBY_URL") || DEFAULT_CONFIG.CLOUDFLARE_STANDBY_URL).replace(/\/+$/, "");

    const candidates = [primaryBase];
    if (standbyBase && standbyBase !== primaryBase) {
      candidates.push(standbyBase);
    }

    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };
    const token = this.getSessionToken();
    if (token && !headers["Authorization"]) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    let lastError = null;

    for (const base of candidates) {
      let path = this.endpoints[endpointKey] || endpointKey;
      if (options.params && typeof options.params === "object") {
        const qs = new URLSearchParams(options.params).toString();
        if (qs) path += (path.includes("?") ? "&" : "?") + qs;
      }
      const url = `${base}${path}`;

      const controller = new AbortController();
      const timeoutMs = options.timeoutMs || 15000;
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

      try {
        const res = await fetch(url, {
          method: options.method || "GET",
          headers,
          body: options.body ? JSON.stringify(options.body) : undefined,
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        // If primary returns a 5xx error, automatically failover to standby worker
        if (res.status >= 500 && candidates.indexOf(base) === 0 && candidates.length > 1) {
          console.warn(`[FloodLock Failover] Primary worker (${base}) returned HTTP ${res.status}. Seamlessly failing over to hot standby: ${standbyBase}`);
          continue;
        }

        const data = await res.json().catch(() => ({}));
        return {
          ok: res.ok,
          status: res.status,
          data,
          worker: base === primaryBase ? "PRIMARY" : "STANDBY"
        };
      } catch (err) {
        clearTimeout(timeoutId);
        lastError = err;
        console.warn(`[FloodLock Failover] Exception on ${base}: ${err.message}. Failing over to next worker slot...`);
      }
    }

    return {
      ok: false,
      status: 0,
      error: lastError ? lastError.message : "All worker nodes unreachable",
      data: null,
      worker: "OFFLINE_FALLBACK"
    };
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

    // 1. Try Primary 24/7 Cloudflare Edge Backend (Worker Slot A)
    const cfUrl = this.get("CLOUDFLARE_EDGE_URL") || DEFAULT_CONFIG.CLOUDFLARE_EDGE_URL;
    if (cfUrl) {
      const res = await timedFetch(`${cfUrl}/health`, 4000);
      if (res && res.ok) {
        try {
          const data = await res.json();
          this.activeBackend = "CLOUDFLARE";
          this.telemetryCache = data;
          return {
            tier: "CLOUDFLARE",
            url: cfUrl,
            name: "CLOUDFLARE PRIMARY EDGE [V8 ACTIVE]",
            data: data
          };
        } catch (e) {
          // JSON parse issue, fall through
        }
      }
    }

    // 2. Try Hot-Standby Cloudflare Edge Backend (Worker Slot B / Redundant Pair)
    const standbyUrl = this.get("CLOUDFLARE_STANDBY_URL") || DEFAULT_CONFIG.CLOUDFLARE_STANDBY_URL;
    if (standbyUrl) {
      const resStandby = await timedFetch(`${standbyUrl}/health`, 3000);
      if (resStandby && resStandby.ok) {
        try {
          const data = await resStandby.json();
          this.activeBackend = "CLOUDFLARE_STANDBY";
          this.telemetryCache = data;
          return {
            tier: "CLOUDFLARE",
            url: standbyUrl,
            name: "CLOUDFLARE HOT-STANDBY EDGE [V8 FAILOVER ACTIVE]",
            data: data
          };
        } catch (e) {
          // Fall through
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

    // 3. Try Direct Local / LAN Backend (only if HTTP to avoid mixed content block, 800ms timeout)
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

    // 4. Try Cloud Serverless API (Hosted directly on Netlify / same origin, 1500ms timeout)
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

    // 5. Try External Cloud Fallback URL (1500ms timeout)
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

    // 6. Pure In-Browser Edge MLP (Zero-Latency Local Physics & Neural Net)
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
window.FLOODLOCK_ENDPOINTS = FLOODLOCK_ENDPOINTS;
