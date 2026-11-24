/**
 * floodlock_frontend/js/config.js
 * ────────────────────────────────────────────────────────────────────────────
 * Central configuration, multi-tier backend failover, and hardware node discovery.
 * 
 * SECURITY MANDATE:
 * API keys (OpenWeather, Tomorrow.io, WorldTides) are strictly kept on the
 * backend server (.env) and NEVER exposed in frontend code.
 */

const WORKER_ENDPOINTS = [
  "https://floodlock-backend.dakshdahore1995.workers.dev",
  "https://floodlock-backend.dahoremugdha.workers.dev",
  "https://floodlock-backend.dakshdadafit.workers.dev",
  "https://floodlock-backend.lanternmech.workers.dev",
  "https://floodlock-backend-standby.dakshdahore1995.workers.dev",
];

const DEFAULT_CONFIG = {
  // Primary 24/7 Cloudflare Edge Backend (Core 1 / Active)
  CLOUDFLARE_EDGE_URL: WORKER_ENDPOINTS[0],

  // Hot Standby Cloudflare Edge Backend (Core 2)
  CLOUDFLARE_STANDBY_URL: WORKER_ENDPOINTS[1],

  // Mirror Alpha Edge Backend (Pool Alpha)
  CLOUDFLARE_MIRROR_ALPHA_URL: WORKER_ENDPOINTS[2],

  // Mirror Beta Edge Backend (Pool Beta)
  CLOUDFLARE_MIRROR_BETA_URL: WORKER_ENDPOINTS[3],

  // Mirror Gamma Edge Backend (Pool Gamma)
  CLOUDFLARE_MIRROR_GAMMA_URL: WORKER_ENDPOINTS[4],
  
  // Local development fallback (strictly active on localhost)
  LOCAL_BACKEND_URL: (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"))
    ? "http://localhost:8000"
    : null,

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
  USER_USAGE: "/api/user/usage",
  USER_API_KEY: "/api/user/api-key",
  FLOOD_FORECAST: "/api/flood/forecast",
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
    this.activeEdgeUrl = null;
    this.isOnline = true;
    this.telemetryCache = null;
    this.endpoints = FLOODLOCK_ENDPOINTS;
  }

  loadFromStorage() {
    for (const key of Object.keys(DEFAULT_CONFIG)) {
      const stored = localStorage.getItem(`FLOODLOCK_${key}`);
      if (stored !== null && stored !== "") {
        // Automatically purge any stale rate-limited worker endpoints from previous sessions
        if (typeof stored === "string" && stored.includes("dakshdahore1995")) {
          localStorage.removeItem(`FLOODLOCK_${key}`);
          continue;
        }
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
      return this.activeEdgeUrl || this.get("CLOUDFLARE_EDGE_URL") || DEFAULT_CONFIG.CLOUDFLARE_EDGE_URL;
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
   * Universal fetch helper with automatic 4-Account Quad-Cluster failover, Bearer token injection, and timeout
   */
  async fetchApi(endpointKey, options = {}) {
    const primaryBase = (this.activeEdgeUrl || this.getBaseUrl()).replace(/\/+$/, "");
    const standbyBase = (this.get("CLOUDFLARE_STANDBY_URL") || DEFAULT_CONFIG.CLOUDFLARE_STANDBY_URL).replace(/\/+$/, "");
    const mirrorAlpha = (this.get("CLOUDFLARE_MIRROR_ALPHA_URL") || DEFAULT_CONFIG.CLOUDFLARE_MIRROR_ALPHA_URL).replace(/\/+$/, "");
    const mirrorBeta = (this.get("CLOUDFLARE_MIRROR_BETA_URL") || DEFAULT_CONFIG.CLOUDFLARE_MIRROR_BETA_URL).replace(/\/+$/, "");
    const mirrorGamma = (this.get("CLOUDFLARE_MIRROR_GAMMA_URL") || DEFAULT_CONFIG.CLOUDFLARE_MIRROR_GAMMA_URL).replace(/\/+$/, "");

    const candidates = [
      primaryBase,
      standbyBase,
      mirrorAlpha,
      mirrorBeta,
      mirrorGamma,
    ].filter((v, i, a) => Boolean(v) && a.indexOf(v) === i);

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

        // If candidate returns 429 (rate-limited) or 5xx, failover to next candidate worker
        if ((res.status === 429 || res.status >= 500) && candidates.length > 1) {
          console.warn(`[FloodLock Failover] Worker (${base}) returned HTTP ${res.status}. Seamlessly shifting traffic to next available cluster...`);
          continue;
        }

        const data = await res.json().catch(() => ({}));
        if (res.ok) {
          this.activeEdgeUrl = base;
        }
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

    // 1. Probe All Cloudflare Edge Backend Clusters (Primary -> Standby -> Mirror Alpha -> Beta -> Gamma)
    const edgeEndpoints = [
      { key: "CLOUDFLARE_EDGE_URL", name: "CLOUDFLARE PRIMARY EDGE [V8 ACTIVE]" },
      { key: "CLOUDFLARE_STANDBY_URL", name: "CLOUDFLARE HOT-STANDBY EDGE [FAILOVER]" },
      { key: "CLOUDFLARE_MIRROR_ALPHA_URL", name: "CLOUDFLARE MIRROR ALPHA [MUGDHA CLUSTER]" },
      { key: "CLOUDFLARE_MIRROR_BETA_URL", name: "CLOUDFLARE MIRROR BETA [DADAFIT CLUSTER]" },
      { key: "CLOUDFLARE_MIRROR_GAMMA_URL", name: "CLOUDFLARE MIRROR GAMMA [LANTERN CLUSTER]" },
    ];

    for (const ep of edgeEndpoints) {
      const url = this.get(ep.key) || DEFAULT_CONFIG[ep.key];
      if (url) {
        const res = await timedFetch(`${url}/health`, 3000);
        if (res && res.ok) {
          try {
            const data = await res.json();
            this.activeBackend = "CLOUDFLARE";
            this.activeEdgeUrl = url;
            this.telemetryCache = data;
            return {
              tier: "CLOUDFLARE",
              url: url,
              name: ep.name,
              data: data
            };
          } catch (e) {}
        }
      }
    }

    // 2. Try Direct Local Backend (only if HTTP and running on localhost, 800ms timeout)
    const localUrl = this.get("LOCAL_BACKEND_URL");
    if (localUrl && typeof window !== "undefined" && window.location && window.location.protocol === "http:") {
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
        } catch (e) {}
      }
    }

    // 3. Try Cloud Serverless API (Hosted directly on Netlify / same origin, 1500ms timeout)
    const currentOrigin = (typeof window !== "undefined" && window.location && window.location.origin) ? window.location.origin : "";
    if (currentOrigin && !currentOrigin.includes("127.0.0.1") && !currentOrigin.includes("localhost")) {
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
        } catch (e) {}
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
        } catch (e) {}
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
window.FLOODLOCK_ENDPOINTS = FLOODLOCK_ENDPOINTS;
