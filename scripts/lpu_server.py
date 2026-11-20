#!/usr/bin/env python3
"""
scripts/lpu_server.py
================================================================================
FloodLock v3.1 — Hardened Localhost-Only Groq LPU Inference Microservice
  - Binds strictly to 127.0.0.1
  - Enforces LPU_AUTH_TOKEN via hmac.compare_digest on all POST requests
  - Restricts CORS to explicit ALLOWED_ORIGIN (never '*')
  - Never prints API key prefixes to stdout
"""

import hmac
import json
import os
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("LPU_PORT", "8000"))
HOST = "127.0.0.1"
LPU_AUTH_TOKEN = os.environ.get("LPU_AUTH_TOKEN", "")
ALLOWED_ORIGIN = os.environ.get("LPU_ALLOWED_ORIGIN", "http://127.0.0.1:3000")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")


def get_groq_key() -> str:
    env_key = os.environ.get("GROQ_API_KEY", "").strip()
    if env_key:
        return env_key
    cred_file = os.path.expanduser("~/.shared-ai-memory/credentials.json")
    if os.path.exists(cred_file):
        try:
            with open(cred_file, "r") as f:
                data = json.load(f)
                return str(data.get("groq_api_key") or data.get("groq_api_keys", {}).get("groq_1") or "")
        except Exception:
            pass
    return ""


GROQ_KEY = get_groq_key()


def call_groq_lpu(prompt: str, model: str = GROQ_MODEL, is_json: bool = True) -> dict:
    if not GROQ_KEY:
        return {"error": "GROQ_API_KEY not configured", "status": "FAILED"}
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are the Lead Hydrological Intelligence Officer for FloodLock. Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 800,
        "reasoning_effort": "none",
    }
    if is_json:
        payload["response_format"] = {"type": "json_object"}

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json", "User-Agent": "FloodLock-LPU/3.1"},
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content) if is_json else {"text": content}
            parsed["_lpu_meta"] = {"model": model, "latency_ms": round((time.time() - t0) * 1000, 2)}
            return parsed
    except Exception:
        return {"error": "Upstream inference request failed", "status": "FAILED"}


class LPURequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Vary", "Origin")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _require_bearer_auth(self) -> bool:
        if not LPU_AUTH_TOKEN or len(LPU_AUTH_TOKEN) < 24:
            self._send_json({"error": "AUTH_NOT_CONFIGURED", "message": "Set LPU_AUTH_TOKEN (>= 24 chars)."}, 503)
            return False
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or not hmac.compare_digest(auth[7:].strip(), LPU_AUTH_TOKEN):
            self._send_json({"error": "UNAUTHORIZED", "message": "Valid Bearer token required."}, 401)
            return False
        return True

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Vary", "Origin")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/health"):
            self._send_json({
                "service": "FloodLock Groq LPU Microservice",
                "version": "3.1.0-Hardened",
                "status": "ONLINE",
                "bind": f"{HOST}:{PORT}",
                "primary_model": GROQ_MODEL,
                "api_key_configured": bool(GROQ_KEY),
                "bearer_auth_enforced": bool(LPU_AUTH_TOKEN and len(LPU_AUTH_TOKEN) >= 24),
            })
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        if not self._require_bearer_auth():
            return
        content_length = min(65536, max(0, int(self.headers.get("Content-Length", 0))))
        raw_body = self.rfile.read(content_length).decode("utf-8", errors="ignore") if content_length > 0 else "{}"
        try:
            body = json.loads(raw_body)
        except Exception:
            self._send_json({"error": "MALFORMED_JSON"}, 400)
            return

        if self.path == "/api/verify":
            prompt = (
                f"Analyze flood event and output JSON: Lat={body.get('lat', 18.998)}, Lon={body.get('lon', 72.842)}, "
                f"Rain={body.get('rain_rate_mm_hr', 85.0)} mm/hr, SoilSat={int(float(body.get('soil_sat', 0.95))*100)}%, "
                f"Surge={body.get('surge_m', 3.5)} m, Depth1h={body.get('depth_cm', 38.0)} cm."
            )
            self._send_json(call_groq_lpu(prompt, model=GROQ_MODEL, is_json=True))
        elif self.path == "/api/chat":
            self._send_json(call_groq_lpu(str(body.get("message", "Status report"))[:2000], model=GROQ_MODEL, is_json=False))
        else:
            self._send_json({"error": "Unknown Endpoint"}, 404)


def run():
    print(f"FloodLock LPU v3.1 on http://{HOST}:{PORT} | Auth Enforced: {bool(LPU_AUTH_TOKEN)}")
    HTTPServer((HOST, PORT), LPURequestHandler).serve_forever()


if __name__ == "__main__":
    run()
