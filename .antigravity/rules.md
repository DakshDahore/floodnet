# MANDATORY LEGAL & GEMINI API COMPLIANCE RULES — FLOODLOCK

1. **No Preview Models in Production:** Never configure or deploy Gemini models labeled `-preview` or `-exp` in production endpoints. Use only stable GA model IDs (e.g. `gemini-1.5-flash`, `gemini-1.5-pro`).
2. **Server-Side API Keys Only:** Never expose `GEMINI_API_KEY` in client-side bundles, frontend environment variables, or public git commits. Route strictly via Cloudflare Workers / backend.
3. **Strict 18+ Age Gate:** Maintain persistent age verification on user onboarding before permitting AI queries.
4. **Safety Filters & Guardrails:** Enforce input sanitization (`sanitizePromptInput`) to redact sensitive PII (Aadhaar, phone numbers, banking coordinates) before sending to any LLM.
5. **Universal AI Disclaimer:** Ensure visible disclaimers on all AI predictions stating content is experimental and advisory.
6. **Commercial Font Safety:** Strictly use SIL Open Font License (OFL) Google Fonts (`Instrument Serif`, `Plus Jakarta Sans`, `JetBrains Mono`). Never deploy demo/non-commercial fonts.
7. **5-Day 50% Refund Policy & Instant Alerts:** Enforce 5-day 50% partial refund guarantee in `/terms` and payment workflows. Dispatch transaction and inquiry alerts directly to `lantern.mech@gmail.com`.

