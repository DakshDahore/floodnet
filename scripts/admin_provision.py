#!/usr/bin/env python3
"""
scripts/admin_provision.py
──────────────────────────────────────────────────────────────────────────────
FloodLock Admin Provisioning Tool (Master Authorization)

Allows Founder Daksh Dahore to instantly upgrade a user's account to Pro or Ultra
upon receiving GPay / UPI payment (₹49 / ₹149) with 100% bank-cleared certainty.

Usage:
  python3 scripts/admin_provision.py user@example.com [pro|ultra]
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

SECRETS_PATH = Path.home() / ".shared-ai-memory" / "floodlock_secrets.json"
PRIMARY_WORKER = "https://floodlock-backend.dakshdahore1995.workers.dev"
STANDBY_WORKER = "https://floodlock-backend-standby.dakshdahore1995.workers.dev"

def load_master_secret():
    if not SECRETS_PATH.exists():
        print(f"[!] Error: Secrets file not found at {SECRETS_PATH}")
        sys.exit(1)
    try:
        with open(SECRETS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("MASTER_SECRET")
    except Exception as e:
        print(f"[!] Error reading secrets: {e}")
        sys.exit(1)

def provision_user(email: str, plan: str = "pro"):
    master_secret = load_master_secret()
    if not master_secret:
        print("[!] Master secret missing from secrets vault.")
        sys.exit(1)

    payload = json.dumps({"email": email.strip().lower(), "plan": plan.strip().lower()}).encode("utf-8")
    
    print(f"\n🌊 [FloodLock Admin Engine] Provisioning '{email}' to {plan.upper()}...")
    
    # Provision on Primary
    req = urllib.request.Request(
        f"{PRIMARY_WORKER}/api/admin/provision-user",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {master_secret}",
            "User-Agent": "FloodLock-Admin-Engine/3.2"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"  ✓ Primary Edge: {data.get('message')}")
            print(f"  ✓ User ID:      {data.get('user_id')}")
            print(f"  ✓ Plan Tier:    {data.get('plan')}")
            print(f"  ✓ Daily Quota:  {data.get('daily_quota')} queries/day")
            print(f"\n✨ Account is ACTIVE worldwide across Cloudflare V8 Isolates + KV!")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        print(f"  [✗] Provisioning failed (HTTP {e.code}): {err_msg}")
        sys.exit(1)
    except Exception as e:
        print(f"  [✗] Network error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/admin_provision.py <email> [pro|ultra]")
        sys.exit(1)
    
    target_email = sys.argv[1]
    target_plan = sys.argv[2] if len(sys.argv) > 2 else "pro"
    provision_user(target_email, target_plan)
