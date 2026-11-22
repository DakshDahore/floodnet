# FloodLock v3.0 Hardened Pack — Deployment & Verification Guide

## Contents
- `CODE_AUDIT_REVIEW_FOR_FOUNDER.md` — Line-by-line Chief Scientist & Security Architect review
- `physics/floodlock_physics_simulator.py` — Mass-conserving Engine 1 hydrology solver (true 6h horizon, CFL sub-stepping, clamped tidal choke, head-driven orifice backwater)
- `physics/test_physics_conservation.py` — Automated conservation & benchmark verification suite
- `cloudflare_worker/` — Production Cloudflare Worker with SQLite Durable Objects, real AES-256-GCM PII encryption, HS256 Bearer auth, 3-Tier AI resilience, and HMAC-verified metered billing
- `security/security_redteam_harness_v3.py` — Honest, zero-false-positive Red-Team verification suite

## Step 1: Rotate Compromised v2 Keys Immediately
Revoke the Groq and Gemini API keys that appeared in `code/backend/index.js` v2 and generate fresh keys.

## Step 2: Verify Physics Locally
```bash
python3 physics/floodlock_physics_simulator.py
python3 physics/test_physics_conservation.py
```

## Step 3: Configure & Deploy Cloudflare Worker
```bash
cd cloudflare_worker
npm install

# Update KV namespace ID in wrangler.jsonc, then set Wrangler secrets (min 32 chars for crypto keys):
npx wrangler secret put MASTER_SECRET
npx wrangler secret put PII_ENCRYPTION_KEY
npx wrangler secret put PAYMENT_WEBHOOK_SECRET
npx wrangler secret put GROQ_API_KEY
npx wrangler secret put GEMINI_API_KEY
# Optional founder alerts:
npx wrangler secret put EMAILJS_SERVICE_ID
npx wrangler secret put EMAILJS_PUBLIC_KEY
npx wrangler secret put EMAILJS_PRIVATE_KEY

# Run locally or deploy to Cloudflare Edge:
npx wrangler dev
npx wrangler deploy
```

## Step 4: Run Honest Red-Team Suite
```bash
python3 security/security_redteam_harness_v3.py https://your-worker.workers.dev
```
