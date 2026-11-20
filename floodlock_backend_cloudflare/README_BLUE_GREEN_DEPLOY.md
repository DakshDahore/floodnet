# FloodLock v3.2 Gold — Zero-Downtime Blue/Green Rolling Deploy Workflow

## 1. Architectural Topology: 2 Workers per Task

FloodLock employs a twin-worker redundant architecture deployed across Cloudflare's global edge:

| Slot | Worker Name | Production URL | Role |
| :--- | :--- | :--- | :--- |
| **Slot A (Primary / Active)** | `floodlock-backend` | `https://floodlock-backend.dakshdahore1995.workers.dev` | Primary active traffic slot |
| **Slot B (Standby / Canary)** | `floodlock-backend-standby` | `https://floodlock-backend-standby.dakshdahore1995.workers.dev` | Hot standby & canary deployment slot |

Both workers share the **exact same strongly consistent state**:
* **Durable Objects**: `SecurityStateDO`, `BillingStateDO`, and `CircuitBreakerDO` are defined in `floodlock-backend` and bound to `floodlock-backend-standby` via `script_name: "floodlock-backend"`. There is zero state divergence between slots.
* **Key-Value Store**: Both slots bind to `FLOODLOCK_KV` (`64ec69f748d3430fb3d34b8d6e59d8c3`).
* **Workers AI**: Both slots bind to Cloudflare Workers AI (`@cf/qwen/qwen2.5-7b-instruct`).

---

## 2. Zero-Downtime Client-Side Failover Matrix (`config.js`)

When the web application (`index.html`, `monitor.html`, `citizen.html`, `admin.html`) executes any API request:
1. **Primary First**: `fetchApi()` dispatches to `CLOUDFLARE_EDGE_URL` (Slot A).
2. **Transparent Hot Failover**: If Slot A times out (> 4500ms), fails with a network exception, or returns `HTTP 5xx`, `config.js` transparently retries the exact request against `CLOUDFLARE_STANDBY_URL` (Slot B) in `< 50ms`.
3. **Sub-Millisecond Edge Floor**: If both network gateways are interrupted (e.g., complete ISP blackouts or catastrophic undersea cable cuts), client execution gracefully shifts to the 209-parameter in-browser Edge MLP (`weights_browser.json`) running locally at 60 FPS (< 0.05ms latency).

---

## 3. Safe Blue/Green Rolling Deployment Protocol

To release a new version (e.g. updating model weights, modifying hydrological routing, or adjusting rate limits) with **zero dropped requests**:

### Step 1: Deploy to Standby Worker (Slot B)
Update and deploy the candidate code to the hot-standby worker first:
```bash
cd floodlock_backend_cloudflare
CLOUDFLARE_API_TOKEN="<TOKEN>" CLOUDFLARE_ACCOUNT_ID="<ACCOUNT_ID>" \
  ./node_modules/.bin/wrangler deploy --config wrangler.standby.jsonc
```

### Step 2: Automated Smoke Tests on Standby
Run synthetic verification against Slot B:
```bash
# Verify health manifest
curl -s -f https://floodlock-backend-standby.dakshdahore1995.workers.dev/health

# Verify ambient telemetry
curl -s -f https://floodlock-backend-standby.dakshdahore1995.workers.dev/api/live-mumbai

# Verify antecedent cache
curl -s -f https://floodlock-backend-standby.dakshdahore1995.workers.dev/api/state-cache
```

### Step 3: Shift Primary Slot / Deploy Primary Worker (Slot A)
Once Slot B passes all smoke tests with 100% success, deploy the update to Slot A:
```bash
CLOUDFLARE_API_TOKEN="<TOKEN>" CLOUDFLARE_ACCOUNT_ID="<ACCOUNT_ID>" \
  ./node_modules/.bin/wrangler deploy --config wrangler.jsonc
```

### Step 4: Verify Both Slots Synchronized
```bash
curl -s https://floodlock-backend.dakshdahore1995.workers.dev/health | jq .version
curl -s https://floodlock-backend-standby.dakshdahore1995.workers.dev/health | jq .version
```

Because clients automatically failover between Slot A and Slot B, **users never experience a single 502, 503, or failed connection while Wrangler uploads and compiles V8 isolates**.

