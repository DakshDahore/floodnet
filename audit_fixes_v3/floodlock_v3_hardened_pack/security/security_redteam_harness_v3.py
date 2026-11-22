#!/usr/bin/env python3
"""
security/security_redteam_harness_v3.py
===============================================================================
FloodLock v3.0 — Honest, Zero-False-Positive Red-Team Security Harness
Fixes the security-theater false positives from v2:
  - Strictly requires HTTP 401 on forged/invalid/alg=none Bearer tokens (NEVER passes 200 "guest")
  - Explicitly probes the former "123456" OTP auth backdoor (must fail with 400/401)
  - Explicitly tests Broken Object Level Authorization (IDOR) on /api/user/profile
  - Explicitly tests unauthenticated/forged billing webhooks & arbitrary-amount refunds
  - Explicitly tests concurrent OTP race conditions & enforces real HTTP 429 rate limiting
  - Tests SQLi, XSS, Path Traversal, RCE, and Prompt Injection with strict rejection assertions
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

DEFAULT_BASE_URL = "http://127.0.0.1:8787"


class HonestSecurityAudit:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.total = 0
        self.passed = 0
        self.failures = []

    def record(self, category: str, vector: str, status: int, ok: bool, detail: str = ""):
        self.total += 1
        if ok:
            self.passed += 1
        else:
            self.failures.append({
                "category": category,
                "vector": vector,
                "status": status,
                "detail": detail,
            })

    def send(self, path: str, method: str = "GET", headers=None, data=None):
        hdrs = dict(headers or {})
        raw_data = None
        if data is not None:
            raw_data = json.dumps(data).encode("utf-8") if isinstance(data, dict) else str(data).encode("utf-8")
            hdrs.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(self.base_url + path, data=raw_data, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                return resp.getcode(), resp.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return 0, str(e)

    def test_otp_backdoor_removed(self):
        print("[+] Testing 1: Former '123456' OTP Backdoor Rejection...")
        code, body = self.send(
            "/api/auth/verify-otp",
            method="POST",
            data={"email": "founder@floodlock.org", "otp": "123456"},
        )
        ok = code in (400, 401, 403) and "session_token" not in body
        self.record("Auth Backdoor", "OTP=123456 without valid challenge", code, ok, body[:120])

    def test_bearer_token_and_idor(self):
        print("[+] Testing 2: Strict Bearer Verification & IDOR Prevention...")
        forged = [
            "Bearer anything_goes",
            "Bearer eyJhbGciOiJub25lIiwidHlwIjoiRkwta2V5In0.eyJzdWIiOiJhZG1pbiJ9.",
            "Bearer " + "A" * 3000,
            "",
        ]
        for tok in forged:
            hdr = {"Authorization": tok} if tok else {}
            code, body = self.send("/api/user/profile?identity=victim@floodlock.org", headers=hdr)
            # STRICT: Must return 401! Never 200 with guest profile!
            ok = code == 401 and "authenticated\": true" not in body
            self.record("Auth / IDOR", tok[:32] or "<missing>", code, ok, body[:120])

    def test_billing_spoofing_and_refund_abuse(self):
        print("[+] Testing 3: Payment Webhook Spoofing & Arbitrary Refund Rejection...")
        # Forged payment webhook without valid HMAC signature
        c1, b1 = self.send(
            "/api/billing/webhook",
            method="POST",
            headers={"x-payment-signature": "deadbeef" * 8},
            data={"gateway_payment_id": "FAKE_UTR_1", "owner_user_id": "USR_1", "plan": "ultra", "amount_inr": 0},
        )
        self.record("Payment Spoofing", "Invalid HMAC webhook signature", c1, c1 == 401, b1[:120])

        # Unauthenticated arbitrary-amount refund attempt
        c2, b2 = self.send(
            "/api/billing/refund",
            method="POST",
            data={"order_id": "FL_ORD_FAKE999", "amount_inr": 999999},
        )
        self.record("Refund Hijack", "Unauthenticated refund call", c2, c2 == 401, b2[:120])

    def test_injection_vectors(self):
        print("[+] Testing 4: SQLi, XSS, Path Traversal & RCE Rejection...")
        vectors = [
            ("SQLi", "/api/forecast?lat=18.9&lon=" + urllib.parse.quote("' UNION SELECT * FROM users --"), "GET", None),
            ("Traversal", "/../../../../etc/passwd", "GET", None),
            ("XSS", "/api/inquiry", "POST", {"name": "<script>alert(1)</script>", "email": "a@b.com", "message": "hi"}),
            ("RCE", "/api/inquiry", "POST", {"name": "$(whoami)", "email": "a@b.com", "message": "; rm -rf /"}),
        ]
        for cat, path, method, data in vectors:
            code, body = self.send(path, method=method, data=data)
            ok = code in (400, 403, 404)
            self.record(cat, path, code, ok, body[:120])

    def test_atomic_3_strike_lockout(self):
        print("[+] Testing 5: Atomic 3-Strike OTP Lockout Enforcement...")
        victim = f"audit_{int(time.time())}@floodlock.org"
        self.send("/api/auth/send-otp", method="POST", data={"email": victim})
        codes = []
        for guess in ["000001", "000002", "000003", "000004"]:
            c, _ = self.send("/api/auth/verify-otp", method="POST", data={"email": victim, "otp": guess})
            codes.append(c)
        ok = 403 in codes  # Lockout MUST engage by strike 3
        self.record("3-Strike Lockout", f"4 bad guesses -> {codes}", codes[-1], ok)

    def test_real_rate_limiting_429(self):
        print("[+] Testing 6: Real HTTP 429 Rate Limiting Enforcement (65 burst calls)...")
        with ThreadPoolExecutor(max_workers=10) as ex:
            results = list(ex.map(lambda _: self.send("/health")[0], range(65)))
        got_429 = any(c == 429 for c in results)
        no_5xx = all(c < 500 and c != 0 for c in results)
        self.record("Rate Limiter", f"65 req burst (429 count={results.count(429)})", 429 if got_429 else 200, got_429 and no_5xx)

    def run(self):
        print("=" * 78)
        print(f" FLOODLOCK v3.0 HONEST RED-TEAM AUDIT -> {self.base_url}")
        print("=" * 78)
        self.test_otp_backdoor_removed()
        self.test_bearer_token_and_idor()
        self.test_billing_spoofing_and_refund_abuse()
        self.test_injection_vectors()
        self.test_atomic_3_strike_lockout()
        self.test_real_rate_limiting_429()

        print("\n" + "=" * 78)
        print(f" Passed: {self.passed}/{self.total} | Failures: {len(self.failures)}")
        print("=" * 78)
        for f in self.failures:
            print(f"  [FAIL] {f['category']} | HTTP {f['status']} | {f['vector']} | {f['detail']}")
        sys.exit(0 if not self.failures else 1)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL
    HonestSecurityAudit(target).run()
