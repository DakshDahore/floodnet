# ⚖️ FLOODLOCK LEGAL & COMPLIANCE CHARTER
**Version**: 1.0.0 (Production Startup Tier)  
**Jurisdiction Compliance**: Digital Personal Data Protection Act (DPDP India 2023), GDPR, CCPA, Google Gemini API Terms of Service, Open Font License (OFL).

---

## 1. Absolute Zero-Hazard Legal Foundations

### A. Font Licensing Protection (CRITICAL FINDING)
* **The Risk**: The three uploaded font packages (`Friends n Fellows 2`, `Moralana`, `Orange Avenue`) are explicitly stamped with **"DEMO / PERSONAL USE ONLY — STRICTLY FORBIDDEN FOR COMMERCIAL USE"**. Automated crawlers from font foundries scan commercial websites (especially sites with pricing tables) and issue statutory copyright infringement claims reaching upwards of $150,000 per violation.
* **The Safeguard**: In all commercial production code and public deployments, FloodLock strictly uses **SIL Open Font License (OFL)** Google Fonts that match the exact same luxury leather/editorial aesthetic:
  * **Display Serif**: `Instrument Serif` / `Cormorant Garamond` (100% royalty-free, legal for commercial sales).
  * **Interface Sans**: `Plus Jakarta Sans` / `Cabinet Grotesk` (clean, non-cursive, ultra-modern luxury).
  * **Telemetry Mono**: `JetBrains Mono` / `Geist Mono` (open-source technical readability).

---

### B. Google Gemini API Production Compliance
In accordance with Google's Master Legal Blueprint for Antigravity IDE:
1. **Zero Preview Models**: All production inference routes strictly to stable, Generally Available (GA) identifiers (e.g. `gemini-1.5-flash`, `gemini-1.5-pro`). Never use `-preview` or `-exp` in production endpoints.
2. **Server-Side API Key Shielding**: `GEMINI_API_KEY` is loaded strictly inside server-side environments (Cloudflare Workers Secrets / Supabase Vault). Zero exposure in Vite or client bundles.
3. **Mandatory 18+ Age Gate**: A hard legal confirmation modal on onboarding requiring users to verify they are $\ge 18$ years of age and accept the Terms & Privacy Policy before any AI interaction is unlocked.
4. **Safety & Moderation Middleware**: PII scrubbing (`sanitizePromptInput`) strips Indian Aadhaar, phone numbers, emails, and financial coordinates prior to calling LLM APIs. Safety filters enforced.
5. **Universal AI Disclaimer**: Embedded persistently on all simulation, tactical map, and chat views:
   > *"AI-generated predictions and hydrological alerts are experimental simulations and may contain inaccuracies. FloodLock is an advisory decision-support tool and must not replace official municipal evacuation or disaster orders."*
6. **No Distillation Clause**: Zero Gemini outputs shall be utilized to distill or train derivative weights.

---

### C. Commercial Terms, Payments & Refund Policy
1. **Pricing**:
   * **Free Tier**: Limited daily quota (e.g., 50 API calls/day, read-only tactical briefing).
   * **Premium Tier (₹49 - ₹79 / month)**: High-frequency API key, full map filters, daily quota refresh.
   * **Ultra Tier (₹149 - ₹199 / month)**: Developer-grade burst limits, interactive AI consultation, webhooks.
   * **Pay-As-You-Go / Enterprise**: Custom volume pricing via founder direct inquiry.
2. **Payment Flow & Verification**:
   * Indian UPI / GPay direct QR routing with automated transaction reference validation (`UPI Ref / UTR ID`) stored in a secure JSON ledger on Supabase.
3. **5-Day 50% Partial Refund Policy**:
   * Due to real-time edge bandwidth, API gateway allocation, and compute costs consumed upon account provisioning, refunds requested **strictly within 5 calendar days** of purchase are eligible for a **50% partial refund**.
   * No refunds are granted after 5 calendar days or if API consumption exceeds 20% of tier quota.
4. **Automated Founder Transaction Alerts**:
   * Every checkout initiation, UPI reference submission, and custom enterprise inquiry automatically triggers a high-priority email alert to `lantern.mech@gmail.com`.
4. **Beta / Experimental Transparency**:
   * Public disclosure on entry page: *"FloodLock v3 is under active beta development. User simulation telemetries may be analyzed by engineers for neural network calibration. In the event of gateway payment latency or bounce, automated retry mechanisms and 24/7 founder support are provided."*

