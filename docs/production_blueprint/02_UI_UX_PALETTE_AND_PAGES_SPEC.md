# 🎨 FLOODLOCK LUXURY UI/UX PALETTE & PAGES SPECIFICATION
**Design Language**: Executive Editorial / Architectural Tech  
**Inspiration**: Savile Row Tailoring (Obsidian Coat, Warm Cognac Leather, Linen White Shirt) + Cupertino Liquid Glass.

---

## 1. Official Color Harmony (Derived from Uploaded Palette)

```css
:root {
  /* THE COAT & LEATHER HARMONY */
  --c-obsidian-coat:   #16100B; /* Deepest Espresso Black (Dark Coat) */
  --c-smoked-umber:    #35281E; /* Rich Outerwear Umber */
  --c-saddle-cognac:   #92542B; /* Warm Polished Leather (Primary CTA / Magnetic Focus) */
  --c-slate-sage:      #788279; /* Muted Technical Grey-Green (Subtle borders, status) */
  --c-beige-leather:   #D6C5B3; /* Light Coffee Cream (Card surfaces, secondary badges) */
  --c-linen-white:     #F8F5EE; /* Crisp Shirt White (Clean backgrounds, high-contrast text) */

  /* SEMANTIC ACCENTS */
  --c-alert-amber:     #C87D32; /* Hydrological Sluice Warning */
  --c-danger-crimson:  #8B2626; /* Catastrophic Inundation */
  --c-safe-olive:      #4D6348; /* Sluice Discharged / Safe Basin */
}
```

---

## 2. Typography Matrix (Strictly Commercial & Royalty-Free)

| Hierarchy | Typeface | Classification | License | Psychological Intent |
| :--- | :--- | :--- | :--- | :--- |
| **Headline Display** | `Instrument Serif` / `Cormorant` | Editorial Serif | SIL OFL (100% Free) | High-fashion authority, serious scientific prestige. Non-cursive. |
| **Interface & Body** | `Plus Jakarta Sans` | Modern Neo-Grotesque | SIL OFL (100% Free) | Apple/Stripe-tier clarity, frictionless legibility, zero clutter. |
| **Data & Code** | `JetBrains Mono` | Monospaced | Apache 2.0 (Free) | Developer authenticity in the API Playground and telemetry readouts. |

---

## 3. The Interactive Liquid Dock (Apple-Inspired Floating Nav)
Inspired by Cupertino's fluid island interactions:
* Floats symmetrically at the bottom of the viewport on mobile, and side/bottom dock on desktop.
* Backed by `backdrop-filter: blur(24px) saturate(180%)` with a micro-border of `--c-beige-leather` at 20% opacity.
* Active pill uses a spring animation (`cubic-bezier(0.16, 1, 0.3, 1)`): expands and glides effortlessly when tapping between sections.
* **100% Hardware-Accelerated (Zero Lag)**: Uses CSS transforms and composite layer rendering, avoiding expensive layout repaints on mobile devices.

---

## 4. Complete Seven-Page Slogan & Structural Map

### Page 1: `/` — The Narrative & Scientific Welcome Deck
* **Hero**: *"FLOODLOCK — AI-Powered Disaster Intelligence for Urban Basins."*
* **The Interrogative Journey**:
  1. *What are urban floods?* $\implies$ Direct 2-line physical breakdown of impervious surfaces vs. drainage chokepoints.
  2. *Why do I need to monitor them?* $\implies$ Curated metrics, live telemetry cards, and direct citations to historical disaster casualty reports.
  3. *How does FloodLock solve this?* $\implies$ The 3-Tier Pipeline: Multi-source Ingestion $\to$ Hydrological Neural Network $\to$ LLM Tactical Evacuation Guidance.
  4. *Why AI over legacy physics simulations?* $\implies$ Traditional CFD (Computational Fluid Dynamics) takes 14 hours per forecast. FloodLock's custom neural net computes street inundation in **12 milliseconds**.
  5. *Experimental Beta Notice*: Transparent data policy notice and founder support link.
* **CTA**: High-contrast, magnetic "Launch Tactical Command" button styled in polished saddle leather (`--c-saddle-cognac`).

### Page 2: `/auth` — Bubble Glass Authentication
* **Providers**: Google 1-Click OAuth, GitHub, and Passwordless Email Magic Link via Supabase.
* **Mandatory 18+ Verification Modal**: Checkbox required before submission to comply with Gemini API production terms.

### Page 3: `/dashboard` — Tactical Citizen & Municipal Deck
* **Real Global Vector Map**: MapLibre GL / OpenStreetMap (high-definition vector roads, building footprints, and elevation contours).
* **Multi-Layer Toggle Dock**:
  * Precipitation radar intensity (mm/hr)
  * Atmospheric instability (CAPE J/kg)
  * Soil moisture saturation (%)
  * Drainage conduits & gravitational sluice gates
* **AI Live Tactical Briefing**: Dynamic 1-to-10 sentence briefing generated from live station telemetry. (Pro & Ultra subscribers can chat with the advisory bot for evacuation routing).

### Page 4: `/models` — Open Source Model Zoo & Datasets
* Dedicated scientific repository.
* Downloadable PyTorch `.pt`, ONNX, and lightweight GGUF binaries (1B–3B parameters) with beginner-friendly 5-line Python execution scripts.
* Raw & synthetic hydrological simulation CSV benchmarks.
* A warm, prestigious **"Thank You for Advancing Climate Science"** contributor acknowledgement.

### Page 5: `/developers` — API Playground & Console
* Self-service API key provisioning (`fl_live_...`).
* Live quota tracker bar (Usage / Daily Limit) with automatic midnight refresh counter.
* Interactive cURL / Python / Node.js code generator for:
  * `/api/v1/rain/estimate` (Precipitation & cloudburst probability)
  * `/api/v1/basin/backflow` (Tidal lock & sluice resistance index)
  * `/api/v1/inundation/depth` (Predicted street water level in cm)

### Page 6: `/pricing` — Commercial Tiers & Direct GPay / UPI Checkout
* Clear side-by-side comparison matrix.
* Automated UPI QR generation for Indian mobile payment with transaction verification reference input.
* Prominent 5-day money-back guarantee banner.

### Page 7: `/legal` — Zero-Hazard Terms, Privacy & Disclaimers
* Comprehensive GDPR / Indian DPDP terms.
* Mandatory Gemini API AI disclaimers and limitation of emergency liability.

