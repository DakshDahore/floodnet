```markdown
# 01 — 4K ULTRA-HD UI/UX DESIGN & ARCHITECTURE SPECIFICATION
**Target Directory:** `/home/daksh/Documents/Projects/floodlock/floodlock_frontend`

This specification translates the 5 uploaded human design references into strict visual and functional requirements.

---

## 1. DESIGN GUARDRAILS (MANDATORY)
1. **THEMED MONOCHROMATIC MAP CANVAS:**
   - Force the map canvas to be 100% monochromatic (CartoDB Dark Matter `dark_all` in Dark Mode; CartoDB Positron `light_all` / Alidade Smooth in Light Mode; plus dark-tinted 3D Cesium OSM Buildings & Terrain when `CESIUM_ION_TOKEN` is provided)[cite: 1, 3].
   - **NEVER** render default consumer green/yellow street maps.
2. **CHROMATIC RESTRAINT & DUAL THEME (DARK + LIGHT MODE):**
   - **Dark Mode (Default):** Background `#080a0f`, Panel surface `#0e121a`, Recessed surface `#0b0e14`, Crisp structural borders `1px solid #1e2636`[cite: 1, 4, 5].
   - **Light Mode (Technical Daylight):** Background `#f1f5f9`, Panel surface `#ffffff`, Recessed surface `#f8fafc`, Crisp structural borders `1px solid #cbd5e1`[cite: 3].
   - **Functional Severity Tokens Only:** Intense colors are strictly reserved for operational telemetry states[cite: 2, 4]:
     - Nominal / Sluice Open: Emerald `#10b981` & Tactical Cyan `#06b6d4`[cite: 4, 5]
     - Elevated / Choke Warning: Amber `#f59e0b`[cite: 1, 4]
     - Critical Surcharge / Hydraulic Lock: Crimson `#ef4444`[cite: 2, 3]
3. **STRUCTURED NESTED CSS GRID:**
   - Zero floating unbordered cards. All sidebars, telemetry cells, and bottom bento strips must sit inside a razor-sharp CSS Grid (`gap: 1px` border grid or `1px solid` cell framing) with uniform `16px` internal padding.
4. **TYPOGRAPHY HIERARCHY:**
   - **Monospace (`JetBrains Mono` / `SF Mono`):** Mandatory for all numeric telemetry, GPS coordinates, pressure hPa, wind vectors, countdown timers, and inference latency badges.
   - **Sans-Serif (`Inter` / `Geist`):** Mandatory for technical headers, navigation labels, and municipal SOP directives.
   - **Editorial Serif Italic (`Instrument Serif` / `Playfair Display` italic):** Used exclusively in the 4K Hero Entrance headline on the words *"ASSISTIVE AI"* (matching Reference Image 1)[cite: 1].

---

## 2. VIEW 1: 4K CINEMATIC ENTRANCE HERO & ARCHITECTURE EXPLAINER
Inspired directly by **Reference Image 1 (`Prepared — Faster, smarter emergency response with ASSISTIVE AI`)**[cite: 1]:
1. **4K Atmospheric Storm Video / WebGL Backdrop:**
   - Full-viewport top section featuring a high-resolution dark monsoon storm cloud video/canvas animation with a subtle `48px x 48px` technical coordinate grid overlay (`rgba(56, 189, 248, 0.05)`)[cite: 1].
2. **Top Glassmorphic Navigation Bar:**
   - Left: `FloodLock` shield emblem + live status pill (`NODE: MSI1 / CLOUD SYNCED`)[cite: 1].
   - Center Links: `Command Deck`, `3-Tier Architecture`, `Hydrology & Wind Physics`, `Unseen CSV Audit`.
   - Right Controls: `☀️/🌙 Theme Toggle`, `🔑 API & Node Config`, and primary CTA button `Launch Command Deck ↗`.
3. **Hero Centerpiece:**
   - Headline: `"Faster, smarter flood response with "` + `<span class="serif-italic">ASSISTIVE AI</span>`[cite: 1].
   - Subheadline: *"Autonomous compound flood forecasting for Mumbai's F-South Ward. Powered by dual physics-informed neural networks, wind-surge harmonics, and locked M2M incident dispatch."*
   - Two CTA Pills: `Enter Live Command Deck ↗` (Solid white/high-contrast pill) and `Explore Architecture ↓` (Glass dark pill)[cite: 1].
4. **Architecture Pipeline Strip (3-Column Technical Explainer):**
   - Explains the exact system workflow clearly so judges/operators immediately understand the platform:
     - **01 / Multi-Vector Telemetry & Wind Physics:** Ingests real-time precipitation, barometric depression, astronomical tide, InSAR subsidence, and onshore wind vectors.
     - **02 / Dual-Tier Neural Inference:** 209-Parameter Edge MLP running at `<0.05 ms` (60 FPS) in the browser paired with a 737-Parameter Deep Backend MLP verified against 1,000 unseen holdout extremes.
     - **03 / Locked M2M LLM Dispatch:** Zero human chat manipulation. Neural outputs feed directly into a sandboxed `Qwen2.5:0.5B` (162 tok/s) engine to compute A* ambulance bypass routes (`Dadar TT Viaduct +8.5m MSL`) and MCGM pump orders.
5. **Interactive Docked Preview Frame:**
   - Just like Reference Image 1, the lower half of the hero showcases the live Command Deck inside a sleek hardware bezel frame[cite: 1]. Clicking `Launch Command Deck` smoothly transitions the Command Deck into a locked `100vh x 100vw` full-screen workstation (with a button in the top bar to return to the Hero view anytime).

---

## 3. VIEW 2: FULL-SCREEN TACTICAL CRISIS COMMAND DECK
Layout structure combining **Reference Image 1 (Left Incident List)**[cite: 1], **Reference Image 2 (Bottom 4-Card Bento Telemetry Strip)**[cite: 2], **Reference Image 3 (Contour & Exposure Legend)**[cite: 3], **Reference Image 4 (Right Alert & Optimization Cards)**[cite: 4], and **Reference Image 5 (Multi-Panel Telemetry Table)**[cite: 5]:

### A. Top System Telemetry Bar (`height: 52px`)
- Brand title + Ward selector (`MCGM F-SOUTH WARD // HINDMATA — LOVE GROVE PRECINCT`).
- **4 Scenario Mode Switcher Buttons:**
  1. `🟢 LIVE MUMBAI API` (Polls real-time Open-Meteo Mumbai rain, wind speed/direction, pressure & tide)
  2. `🟠 JULY 2023 CLOUDBURST` (`Rain: 92 mm/hr`, `1hr Avg: 85 mm/hr`, `Tide: 4.21m MSL`, `Pressure: 994 hPa`, `Wind: 21.5 m/s @ 245°`)
  3. `🔴 JULY 2005 DISASTER` (`Rain: 190 mm/hr`, `1hr Avg: 165 mm/hr`, `Tide: 4.48m MSL`, `Pressure: 982 hPa`, `Wind: 31.0 m/s @ 250°`)
  4. `🎛️ MANUAL SIMULATOR` (Activates real-time sliders)
- Active Backend Indicator (`LOCAL MSI1 [162 TOK/S]` vs `CLOUD FALLBACK` vs `EDGE 209-MLP`) + `🔔 Notifications Toggle` + `🔑 API Keys` + `☀️/🌙 Theme`.

### B. Left Panel (`width: 340px`): Telemetry Controls & Precinct Nodes
1. **Interactive Physics Sliders (60 FPS Edge Inference):**
   - `Instant Rainfall`: `0` to `195 mm/hr`
   - `1-Hr Rolling Rainfall`: `0` to `180 mm/hr`
   - `Astronomical Tide`: `1.00` to `5.20 m MSL`
   - `Barometric Pressure`: `960` to `1022 hPa`
   - `Wind Speed`: `0` to `35 m/s`
   - `Wind Direction`: `0°` to `360°` (Onshore Worli vector highlighted at `250°`)
   - `InSAR Subsidence`: `0.0` to `35.0 mm/yr` (Default `-14.2 mm/yr`)
2. **Active Sector Incident Feed (Inspired by Reference Image 1 & 5)**[cite: 1, 5]:
   - Live status rows for:
     - `Hindmata Saucer Basin (+1.8m MSL)`
     - `Love Grove Sluice Outfall (+3.0m MSL Invert)`
     - `Dadar TT Elevated Viaduct (+8.5m MSL Bypass)`
     - `KEM Hospital Emergency Corridor (+4.5m MSL)`
     - `Pramod Mahajan Sump Holding Tank`

### C. Center Viewport: Monochromatic 3D/2.5D Map + Bottom 4-Card Bento Strip
1. **Interactive Map Canvas:**
   - Displays multi-ring flood exposure contours (matching Reference Image 3's concentric exposure zones) around Hindmata Junction[cite: 3].
   - **Love Grove Outfall Culvert Vector:** Connects Hindmata (`72.8430° E`) west to Worli Seaface (`72.8165° E`). Glows **Emerald (`#10b981`)** when `Effective Tide < 2.8m`, **Amber (`#f59e0b`)** when choking (`2.8m – 3.0m`), and pulses **Crimson (`#ef4444`)** when `Effective Tide >= 3.0m MSL` (Total Hydraulic Lock).
   - **Evacuation & Ambulance Routing Vectors:**
     - Surface Dr. B.A. Road lane: Turns dashed Crimson (`SEVERED`) when ponding depth $\ge 0.30\text{ m}$.
     - Dadar TT Elevated Viaduct (`+8.5m MSL`): Glows bright Tactical Cyan (`#06b6d4`) as the active flood-immune bypass.
   - **Click-to-Audit Spatial Inspector:** Clicking any point on the map opens a crisp dark glass popover (matching Reference Image 1's center callout card) showing exact lat/lon, ground elevation, water ponding depth, and outfall head delta[cite: 1].
2. **Bottom 4-Card Bento Telemetry Strip (Inspired directly by Reference Image 2)**[cite: 2]:
   - **Bento Card 1 — Population & Ward Exposure:** Shows exposed residents count (e.g., `14,200`) + a 40-block green/amber/red dot-matrix grid indicator[cite: 2].
   - **Bento Card 2 — Outfall Hydraulic Choke Gauge:** Semi-circular radial arc gauge (`0%` to `100%`) showing exact gravity drainage lock at Love Grove Sluice Gates[cite: 2].
   - **Bento Card 3 — Compound Surge & Rain Amp:** Displays `+ΔH_baro` + `+ΔH_wind` in `cm`, effective tide in `m MSL`, and wind-driven precipitation amplification `%`[cite: 2].
   - **Bento Card 4 — Wind Vector Compass Dial:** Interactive rotating vector arrow inside a degree compass (`0°–360°`) displaying wind speed in `m/s` and onshore component toward Mahim/Worli Bay[cite: 2].

### D. Right Panel (`width: 380px`): Dual Neural Audit & Locked M2M LLM Terminal
Inspired by **Reference Image 4 (`Alerts / Optimize / Transit Status`)**[cite: 4]:
1. **Time-to-Inundation Countdown Card:**
   - Huge `JetBrains Mono` digital readout (e.g., `18.4 MIN` or `> 180 MIN NOMINAL`).
   - Side-by-side comparison bar:
     - `Tier-1 Edge MLP (209 Params)`: Value + `<0.05 ms` latency badge.
     - `Tier-2 Deep MLP (737 Params)`: Value + `Unseen Holdout MAE` badge.
2. **Corridor & Transit Status Card (Matching Reference Image 4)**[cite: 4]:
   - Shows impact delay (e.g., `+24 min surface delay` vs `0 min via Dadar TT Viaduct +8.5m MSL`) and a button `Highlight Safe Route on Map`[cite: 4].
3. **System-Only M2M LLM Dispatch Terminal:**
   - Header Badge: `🔒 SYSTEM-ONLY M2M DISPATCH // QWEN2.5:0.5B (USER INPUT LOCKED)`.
   - Zero text box for user prompts.
   - Automatically streams the structured **MCGM F-South Ward Emergency Directive**:
     - `[ALERT LEVEL & HYDRAULIC LOCK SUMMARY]`
     - `[LOVE GROVE & PRAMOD MAHAJAN PUMP ORDERS]`
     - `[KEM HOSPITAL AMBULANCE REROUTING DIRECTIVE]`
     - `[PUBLIC BROADCAST WARNING]`
4. **Background Notification Engine:**
   - Supports browser `Notification.requestPermission()` + sleek sliding HUD alert banners + subtle acoustic warning chime when `ETA < 30 min` or `Outfall Choke >= 85%`.
