import json
import os
import subprocess

CF_BACKEND_DIR = "/home/daksh/Documents/Projects/floodlock/floodlock_backend_cloudflare"
FRONTEND_DIR = "/home/daksh/Documents/Projects/floodlock/floodlock_frontend"
CRED_PATH = "/home/daksh/.shared-ai-memory/credentials.json"

with open(CRED_PATH, "r") as f:
    creds = json.load(f)

# 1. Update all wrangler config files
config_files = [
    "wrangler.jsonc",
    "wrangler.standby.jsonc",
    "wrangler.mirror-alpha.jsonc",
    "wrangler.mirror-beta.jsonc",
    "wrangler.mirror-gamma.jsonc",
]

for cfg in config_files:
    path = os.path.join(CF_BACKEND_DIR, cfg)
    if not os.path.exists(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update FRONTEND_URL to floodlock.pages.dev
    content = content.replace('"FRONTEND_URL": "https://metoflood.netlify.app"', '"FRONTEND_URL": "https://floodlock.pages.dev"')
    
    # Add GITHUB_CLIENT_ID_PAGES if not present
    if '"GITHUB_CLIENT_ID_PAGES"' not in content:
        content = content.replace(
            '"GITHUB_CLIENT_ID": "Ov23liHMgDQduw9y5SOT"',
            '"GITHUB_CLIENT_ID": "Ov23liHMgDQduw9y5SOT",\n    "GITHUB_CLIENT_ID_PAGES": "Ov23li0qner783rsRpZL"'
        )
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {cfg}")

# 2. Update floodlock_frontend/auth/callback/index.html
cb_path = os.path.join(FRONTEND_DIR, "auth/callback/index.html")
with open(cb_path, "r", encoding="utf-8") as f:
    cb_content = f.read()

old_clusters = """      const edgeClusters = [
        "https://floodlock-backend.dahoremugdha.workers.dev",
        "https://floodlock-backend.dakshdadafit.workers.dev",
        "https://floodlock-backend.lanternmech.workers.dev"
      ];"""

new_clusters = """      const edgeClusters = [
        "https://floodlock-backend.dakshdahore1995.workers.dev",
        "https://floodlock-backend.dahoremugdha.workers.dev",
        "https://floodlock-backend.dakshdadafit.workers.dev",
        "https://floodlock-backend.lanternmech.workers.dev"
      ];"""

if old_clusters in cb_content:
    cb_content = cb_content.replace(old_clusters, new_clusters)
    with open(cb_path, "w", encoding="utf-8") as f:
        f.write(cb_content)
    print("Updated auth/callback/index.html with primary cluster at index 0.")

# 3. Update floodlock_frontend/js/config.js
cfg_js_path = os.path.join(FRONTEND_DIR, "js/config.js")
with open(cfg_js_path, "r", encoding="utf-8") as f:
    cfg_js = f.read()

old_endpoints = """const WORKER_ENDPOINTS = [
  "https://floodlock-backend.dahoremugdha.workers.dev",
  "https://floodlock-backend.dakshdadafit.workers.dev",
  "https://floodlock-backend.lanternmech.workers.dev",
  "https://floodlock-backend.dakshdahore1995.workers.dev",
  "https://floodlock-backend-standby.dakshdahore1995.workers.dev",
];"""

new_endpoints = """const WORKER_ENDPOINTS = [
  "https://floodlock-backend.dakshdahore1995.workers.dev",
  "https://floodlock-backend.dahoremugdha.workers.dev",
  "https://floodlock-backend.dakshdadafit.workers.dev",
  "https://floodlock-backend.lanternmech.workers.dev",
  "https://floodlock-backend-standby.dakshdahore1995.workers.dev",
];"""

if old_endpoints in cfg_js:
    cfg_js = cfg_js.replace(old_endpoints, new_endpoints)
    with open(cfg_js_path, "w", encoding="utf-8") as f:
        f.write(cfg_js)
    print("Updated js/config.js with dakshdahore1995 as primary at index 0.")

print("All configuration files synchronized.")

