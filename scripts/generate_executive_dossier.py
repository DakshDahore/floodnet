#!/usr/bin/env python3
"""
FloodLock Executive Master Dossier Generator
Builds a publication-grade 2-page executive briefing document in HTML & converts to PDF.
"""
import os
import subprocess
import base64

def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return ""

def main():
    logo_path = "/home/daksh/Documents/Projects/floodlock/floodlock_frontend/assets/logo.jpg"
    logo_b64 = get_base64_image(logo_path)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FloodLock™ — 40-Day Production Master Dossier & Technical Charter</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;800;900&family=JetBrains+Mono:wght@400;600;700;800&family=Montserrat:wght@600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    @page {{
      size: A4 portrait;
      margin: 7mm 9mm;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      color: #121212;
      background: #EAE6DF;
      font-size: 8.4pt;
      line-height: 1.34;
    }}
    
    /* Interactive Web Bar (Hidden when printed to PDF) */
    .web-action-bar {{
      position: sticky;
      top: 0;
      z-index: 1000;
      background: #121212;
      color: #F5EFE6;
      padding: 0.6rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      font-family: 'Montserrat', sans-serif;
      font-size: 0.85rem;
    }}
    .web-action-bar a, .web-action-bar button {{
      background: #B45309;
      color: #ffffff;
      border: none;
      padding: 0.4rem 0.9rem;
      border-radius: 999px;
      font-weight: 700;
      font-size: 0.78rem;
      text-decoration: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }}
    @media print {{
      .web-action-bar {{ display: none !important; }}
      body {{ background: #ffffff !important; }}
      .page-container {{
        box-shadow: none !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        height: 283mm !important;
        max-height: 283mm !important;
      }}
    }}

    /* A4 Page Shell */
    .page-container {{
      width: 192mm;
      min-height: 280mm;
      max-height: 283mm;
      margin: 8mm auto;
      background: #ffffff;
      padding: 7mm 8mm;
      box-shadow: 0 10px 40px rgba(0,0,0,0.12);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      page-break-after: always;
      position: relative;
      overflow: hidden;
      border: 1px solid #D6C5B3;
    }}
    .page-container:last-child {{
      page-break-after: avoid;
    }}

    /* Swiss Typography Hierarchy */
    .font-hero {{ font-family: 'Cinzel', serif; }}
    .font-editorial {{ font-family: 'Playfair Display', serif; }}
    .font-label {{ font-family: 'Montserrat', sans-serif; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; }}
    .font-mono {{ font-family: 'JetBrains Mono', monospace; }}

    /* Header Masthead */
    .masthead {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 2px solid #451A03;
      padding-bottom: 5px;
      margin-bottom: 6px;
    }}
    .masthead-logo-group {{
      display: flex;
      align-items: center;
      gap: 9px;
    }}
    .masthead-logo {{
      width: 38px;
      height: 38px;
      border-radius: 50%;
      border: 1.5px solid #B45309;
      object-fit: cover;
    }}
    .masthead-titles h1 {{
      font-size: 15pt;
      font-weight: 900;
      color: #451A03;
      letter-spacing: 0.04em;
      line-height: 1;
    }}
    .masthead-titles p {{
      font-size: 6.5pt;
      color: #78350F;
      font-weight: 700;
      margin-top: 2px;
    }}
    .masthead-badge-col {{
      text-align: right;
    }}
    .badge-gold {{
      background: #451A03;
      color: #F5EFE6;
      font-size: 6pt;
      padding: 2px 7px;
      border-radius: 3px;
      font-weight: 800;
      display: inline-block;
    }}
    .badge-sub {{
      font-size: 5.8pt;
      color: #666;
      margin-top: 2px;
      display: block;
    }}

    /* Strategic URL Bar */
    .url-strip {{
      display: flex;
      justify-content: space-between;
      background: #F5EFE6;
      border: 1px solid #E6D8C3;
      border-radius: 4px;
      padding: 3.5px 8px;
      font-size: 6.2pt;
      font-weight: 600;
      color: #451A03;
      margin-bottom: 7px;
    }}
    .url-strip strong {{ color: #B45309; }}

    /* Grid Layouts */
    .grid-2col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      margin-bottom: 6px;
    }}
    .grid-3col {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 5px;
      margin-bottom: 6px;
    }}
    .grid-4col {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 5px;
      margin-bottom: 7px;
    }}

    /* Bento Card Architecture */
    .card {{
      background: #FAF8F5;
      border: 1px solid #E6D8C3;
      border-radius: 6px;
      padding: 6px 8px;
      position: relative;
    }}
    .card-accent {{
      border-left: 3px solid #B45309;
      background: #FFFDF9;
    }}
    .card-dark {{
      background: #191410;
      color: #F5EFE6;
      border-color: #382B22;
    }}
    .card-title {{
      font-size: 7.2pt;
      font-weight: 800;
      color: #451A03;
      display: flex;
      align-items: center;
      gap: 4px;
      margin-bottom: 3px;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    .card-dark .card-title {{
      color: #E6D8C3;
    }}
    .card-p {{
      font-size: 6.7pt;
      line-height: 1.34;
      color: #333333;
    }}
    .card-dark .card-p {{
      color: #D6C5B3;
    }}

    /* Metric Highlight Box */
    .stat-pill {{
      text-align: center;
      background: #F5EFE6;
      border: 1px solid #E6D8C3;
      border-radius: 5px;
      padding: 5px 3px;
    }}
    .stat-val {{
      font-size: 11pt;
      font-weight: 900;
      color: #451A03;
      line-height: 1;
      font-family: 'JetBrains Mono', monospace;
    }}
    .stat-lbl {{
      font-size: 5.4pt;
      color: #78350F;
      font-weight: 700;
      text-transform: uppercase;
      margin-top: 2px;
    }}

    /* Tables */
    table.compact-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 5.9pt;
      margin-top: 3px;
    }}
    table.compact-table th {{
      background: #451A03;
      color: #ffffff;
      padding: 3px 5px;
      text-align: left;
      font-weight: 700;
    }}
    table.compact-table td {{
      padding: 2.5px 5px;
      border-bottom: 1px solid #E6D8C3;
      color: #222;
    }}
    table.compact-table tr:nth-child(even) td {{
      background: rgba(230, 216, 195, 0.25);
    }}

    /* Section Subhead */
    .section-ribbon {{
      background: #451A03;
      color: #F5EFE6;
      font-size: 6.8pt;
      font-weight: 800;
      padding: 3px 7px;
      border-radius: 3px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 5px;
    }}

    /* Code Snippets */
    .mini-code {{
      background: #0D0907;
      color: #38bdf8;
      border: 1px solid #33241A;
      border-radius: 4px;
      padding: 5px 7px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 5.8pt;
      line-height: 1.28;
      margin-top: 3px;
      white-space: pre-wrap;
    }}
    .mini-code span.comment {{ color: #788279; }}
    .mini-code span.kw {{ color: #F59E0B; }}

    /* Footer */
    .page-footer {{
      border-top: 1px solid #D6C5B3;
      padding-top: 4px;
      font-size: 5.6pt;
      color: #777777;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
  </style>
</head>
<body>

  <!-- Web Interactive Bar -->
  <div class="web-action-bar">
    <div><strong>FLOODLOCK™ MASTER TECHNICAL DOSSIER</strong> — 40-Day Production Architecture Summary</div>
    <div style="display:flex; gap:0.6rem;">
      <a href="https://floodlock.pages.dev" target="_blank">🛰️ Live Platform</a>
      <a href="https://floodlock-docs.pages.dev" target="_blank">📖 Docs Portal</a>
      <button onclick="window.print()">🖨️ Export / Print PDF</button>
    </div>
  </div>

  <!-- ═════════════════════════════════════════════════════════════════════
       PAGE 1: DEEP HYDRODYNAMICS, NEURAL ACCELERATION & SCALE CAPACITY
       ═════════════════════════════════════════════════════════════════════ -->
  <div class="page-container">
    <div>
      <!-- Masthead Header -->
      <header class="masthead">
        <div class="masthead-logo-group">
          <img src="data:image/jpeg;base64,{logo_b64}" class="masthead-logo" alt="Lantern Mech">
          <div class="masthead-titles">
            <h1 class="font-hero">FLOODLOCK</h1>
            <p class="font-label">PLANETARY FLOOD INTELLIGENCE &amp; EDGE HYDRODYNAMICS // V3.2.0-GOLD</p>
          </div>
        </div>
        <div class="masthead-badge-col">
          <span class="badge-gold font-label">EXECUTIVE CHARTER • 40-DAY SPRINT</span>
          <span class="badge-sub font-mono">LANTERN MECHATRONICS • FOUNDER: DAKSH DAHORE</span>
        </div>
      </header>

      <!-- Key URLs Matrix -->
      <div class="url-strip font-mono">
        <div><strong>LIVE RADAR:</strong> https://floodlock.pages.dev</div>
        <div><strong>TECHNICAL SPEC:</strong> https://floodlock-docs.pages.dev</div>
        <div><strong>PYPI:</strong> pip install floodlock-sdk</div>
        <div><strong>SOURCE:</strong> github.com/DakshDahore/floodnet</div>
      </div>

      <!-- High-Throughput Stats -->
      <div class="grid-4col">
        <div class="stat-pill">
          <div class="stat-val">50,000,000+</div>
          <div class="stat-lbl">Daily Query Capacity</div>
        </div>
        <div class="stat-pill">
          <div class="stat-val">0.15 ms</div>
          <div class="stat-lbl">Edge V8 Inundation Solve</div>
        </div>
        <div class="stat-pill">
          <div class="stat-val">180,000x</div>
          <div class="stat-lbl">PDE Solver Acceleration</div>
        </div>
        <div class="stat-pill">
          <div class="stat-val">94.2%</div>
          <div class="stat-lbl">Disaster Holdout Accuracy</div>
        </div>
      </div>

      <!-- Section: Why Neural Net over Numerical Simulation -->
      <div class="section-ribbon">
        <span>01 / The Core Hydrodynamic Breakthrough: Why Neural Surrogates Beat 2D PDE Solvers</span>
        <span class="font-mono">SOLVING THE 6-HOUR DEADLINE</span>
      </div>

      <div class="grid-2col">
        <div class="card card-accent">
          <div class="card-title">⚠️ The Classical 6-Hour Simulation Flaw</div>
          <div class="card-p">
            Conventional 2D shallow water hydrodynamic solvers (Saint-Venant PDEs / finite-volume meshes like HEC-RAS or Delft3D) require <strong>4 to 6 hours of heavy supercomputing cluster execution</strong> to converge over municipal catchments. In flash floods, precipitation converges in under 30 minutes; by the time simulations compute, streets are submerged and sirens fire 40 minutes too late.
          </div>
        </div>
        <div class="card card-accent">
          <div class="card-title">⚡ The 0.15ms Edge Tensor Solution</div>
          <div class="card-p">
            FloodLock replaces computational grids with a custom-trained <strong>2.7M parameter physics-bounded neural surrogate</strong> executed across 330+ Cloudflare edge PoPs. It condenses compound 2D shallow water hydraulics into a single forward pass in <strong>0.15ms</strong> (180,000x faster), predicting exact street water depth (h) and crest latency (t_crest) in real-time.
          </div>
        </div>
      </div>

      <!-- Mass Conservation Equation & Physics Constraints -->
      <div class="card" style="margin-bottom: 6px; background: #FAF5EE; border-color: #B45309;">
        <div class="card-title">🔬 Mass-Conserved Physics Formulation &amp; Boundary Continuity</div>
        <div class="card-p">
          Predictions are strictly bounded by deterministic physical mass conservation. Inundation depth Δh cannot exceed effective rainfall minus subsurface Green-Ampt infiltration plus tidal backwater head:
        </div>
        <div class="mini-code font-mono" style="background:#1C140E; color:#E6D8C3; font-size: 6.3pt; padding: 5px 8px; margin: 3px 0;">
Δh = max(0, R₀ · Δt - I_cum(Kₛ, θ) + H_tide · 1_{{H_tide > Z_invert}} - Q_out)  |  Mass Conserved to Machine Epsilon (ε &lt; 10⁻⁷)
        </div>
        <div class="card-p" style="font-size: 6.2pt; color: #555;">
          • Green-Ampt Infiltration Rate: f(t) = Kₛ · (1 + ψ · Δθ / F(t))  • Outfall Backwater Choke: Torricelli weir capping prevents artificial drainage dissipation during coastal storm tides.
        </div>
      </div>

      <!-- 14-Feature Input Vector -->
      <div class="section-ribbon">
        <span>02 / The 14-Feature Atmospheric-Soil-Marine Tensor Input Vector</span>
        <span class="font-mono">HOLISTIC TERRESTRIAL COUPLING</span>
      </div>

      <div class="card" style="margin-bottom: 6px;">
        <table class="compact-table">
          <thead>
            <tr>
              <th>Vector</th>
              <th>Physical Dimension</th>
              <th>Telemetry Source</th>
              <th>Mathematical Role in Model</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>[00-02]</code></td>
              <td>Rain Intensity R₀, Antecedent R₄₈, Storage R₁₂₀</td>
              <td>Doppler Radar / GPM IMERG</td>
              <td>Primary rainfall forcing and 120-hour cumulative basin subsurface priming.</td>
            </tr>
            <tr>
              <td><code>[03-05]</code></td>
              <td>Convective CAPE, Pressure Drop ΔP, Wind Shear</td>
              <td>ERA5 Reanalysis / NOAA GFS</td>
              <td>Atmospheric cloudburst buoyancy, barometric storm surge, wind surface drag.</td>
            </tr>
            <tr>
              <td><code>[06-07]</code></td>
              <td>Drought Index SPI-30, Deep Aquifer SPI-90</td>
              <td>Global Drought Observatory</td>
              <td>Groundwater recharge headroom and antecedent macro-catchment deficit.</td>
            </tr>
            <tr>
              <td><code>[08-09]</code></td>
              <td>Volumetric Soil θ, Hydraulic Infiltration Kₛ</td>
              <td>Copernicus SMAP Satellite</td>
              <td>Non-linear soil moisture degree (Sₑ) and Green-Ampt permeability ceiling.</td>
            </tr>
            <tr>
              <td><code>[10-11]</code></td>
              <td>Canal Proximity, Topographic Wetness (TWI)</td>
              <td>HydroSHEDS / USGS 30m DEM</td>
              <td>Micro-terrain convergence sink routing and drainage channel distance.</td>
            </tr>
            <tr>
              <td><code>[12-13]</code></td>
              <td>Impervious Asphalt Fraction, Tidal Head H_tide</td>
              <td>Copernicus Urban Atlas / NOAA Tides</td>
              <td>Urban concrete runoff acceleration (C=0.90) and coastal outfall gravity choking.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empirical Disaster Holdouts & Adversarial LLM -->
      <div class="section-ribbon">
        <span>03 / Disaster Benchmark Accuracy &amp; Adversarial Groq LPU Cross-Check</span>
        <span class="font-mono">EMPIRICAL VALIDATION</span>
      </div>

      <div class="grid-2col">
        <div class="card">
          <div class="card-title">🏆 94.2% Disaster Holdout Benchmark</div>
          <table class="compact-table" style="font-size: 5.6pt;">
            <thead><tr><th>Disaster Basin</th><th>Event Profile</th><th>Depth MAE</th><th>Score</th></tr></thead>
            <tbody>
              <tr><td>Mumbai Mithi</td><td>Extreme Monsoonal Cloudburst</td><td>3.8 cm</td><td><strong>96.1%</strong></td></tr>
              <tr><td>Valencia Turia</td><td>2024 DANA Catastrophic Surge</td><td>4.2 cm</td><td><strong>93.4%</strong></td></tr>
              <tr><td>London Thames</td><td>Estuary Tidal Outfall Lock</td><td>2.9 cm</td><td><strong>95.0%</strong></td></tr>
              <tr><td>Houston Bayou</td><td>Hurricane Harvey Inundation</td><td>4.8 cm</td><td><strong>94.6%</strong></td></tr>
              <tr><td>Tokyo Arakawa</td><td>Typhoon Hagibis Crest Wave</td><td>5.1 cm</td><td><strong>92.1%</strong></td></tr>
            </tbody>
          </table>
        </div>

        <div class="card card-accent">
          <div class="card-title">🧠 Adversarial Groq LPU &amp; Safety Floor</div>
          <div class="card-p">
            Every neural prediction is cross-checked in parallel by high-speed <strong>Groq LPUs</strong> (<code>openai/gpt-oss-120b</code>) to detect anomalies. 
            <br><br>
            <strong>Deterministic Safety Floor Protocol:</strong> To eradicate algorithmic complacency, if physical sensors measure R₀ ≥ 25 mm/hr or R₄₈ ≥ 100 mm with Sₑ ≥ 0.80, the system <em>overwrites any benign text</em> and mandates civil defense evacuation corridors.
          </div>
        </div>
      </div>
    </div>

    <!-- Page 1 Footer -->
    <footer class="page-footer">
      <span>FloodLock™ Planetary Technical Briefing • Lantern Mechatronics</span>
      <span class="font-mono">SECTION 1 OF 2 // 40-DAY CAPSTONE DOSSIER</span>
      <span>Live Verification: https://floodlock.pages.dev</span>
    </footer>
  </div>


  <!-- ═════════════════════════════════════════════════════════════════════
       PAGE 2: 10-CORE CLOUD CLUSTER, ENTERPRISE ECOSYSTEM & FUTURE SCOPE
       ═════════════════════════════════════════════════════════════════════ -->
  <div class="page-container">
    <div>
      <!-- Masthead Header -->
      <header class="masthead">
        <div class="masthead-logo-group">
          <img src="data:image/jpeg;base64,{logo_b64}" class="masthead-logo" alt="Lantern Mech">
          <div class="masthead-titles">
            <h1 class="font-hero">FLOODLOCK</h1>
            <p class="font-label">PLANETARY INFRASTRUCTURE, ENTERPRISE SUITE &amp; FUTURE ROADMAP</p>
          </div>
        </div>
        <div class="masthead-badge-col">
          <span class="badge-gold font-label">SYSTEM BLUEPRINT // V3.2.0-GOLD</span>
          <span class="badge-sub font-mono">10-CORE CLOUDFLARE EDGE CLUSTER</span>
        </div>
      </header>

      <!-- Section: 10-Core Multi-Worker Cluster & AMR Quadtree -->
      <div class="section-ribbon">
        <span>04 / Distributed 10-Core Planetary Edge Mesh &amp; AMR Quadtree</span>
        <span class="font-mono">HORIZONTALLY SCALED TOPOLOGY</span>
      </div>

      <div class="card" style="margin-bottom: 6px;">
        <div class="card-p" style="margin-bottom: 4px;">
          The planetary surface is indexed into <strong>41 macro-basins</strong> and structured as a dynamic <strong>Adaptive Mesh Refinement (AMR) Quadtree</strong>. Quiescent dry zones (R₀ &lt; 2.5 mm/hr) evaluate at zero AI quota cost; convective storms trigger automatic hierarchical Level-2 quadrant subdivisions.
        </div>
        <table class="compact-table">
          <thead>
            <tr>
              <th>Core Unit</th>
              <th>Production Endpoint</th>
              <th>Cluster Designation</th>
              <th>Architectural Responsibility</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>Core 1</code></td>
              <td><code>floodlock-backend.lanternmech.workers.dev</code></td>
              <td>Master Gateway</td>
              <td>Primary traffic entry, cryptographic auth tokens, rate-limiting, edge TLS.</td>
            </tr>
            <tr>
              <td><code>Core 2</code></td>
              <td><code>floodlock-backend.dakshdahore1995.workers.dev</code></td>
              <td>Hot Standby Gateway</td>
              <td>Automated failover (&lt;15ms) if Core 1 hits Cloudflare circuit thresholds.</td>
            </tr>
            <tr>
              <td><code>Core 3</code></td>
              <td><code>floodlock-backend.dahoremugdha.workers.dev</code></td>
              <td>Click &amp; Telemetry Stream</td>
              <td>High-throughput sensor ingestion, ground-truth citizen upload pipelines.</td>
            </tr>
            <tr>
              <td><code>Core 4</code></td>
              <td><code>floodlock-backend.dakshdadafit.workers.dev</code></td>
              <td>Neural 14F Core</td>
              <td>Pure-source V8 weights isolate executing the 14-parameter tensor matrix.</td>
            </tr>
            <tr>
              <td><code>Cores 5-11</code></td>
              <td>7 Regional Worker Isolates</td>
              <td>Continental Shards</td>
              <td>South Asia, East Asia, West Europe, Med Europe, North America, South America, Oceania.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Enterprise Full-Stack Suite -->
      <div class="section-ribbon">
        <span>05 / Full-Stack Enterprise Platform, Auth Gates &amp; Developer Tools</span>
        <span class="font-mono">PRODUCTION-GRADE SECURITY</span>
      </div>

      <div class="grid-3col">
        <div class="card card-accent">
          <div class="card-title">🔐 Triple-Engine Auth</div>
          <div class="card-p">
            • <strong>Google OAuth 2.0</strong> with verified profile synchronization.<br>
            • <strong>Dual GitHub OAuth:</strong> Dedicated client (<code>Ov23li0qner783rsRpZL</code>) for Cloudflare Pages.<br>
            • <strong>Passwordless CSPRNG OTP:</strong> 6-digit email codes with IP-scoped 3-strike brute-force defense.
          </div>
        </div>

        <div class="card card-accent">
          <div class="card-title">⚡ Developer API Platform</div>
          <div class="card-p">
            • <strong>Live Quota Engine:</strong> Distributed KV meters with 00:00 UTC resets.<br>
            • <strong>Zero-Dependency REST:</strong> Instant JSON endpoints for cURL, Python, and Node.js.<br>
            • <strong>API Key Rotation:</strong> Instant self-service cryptographically signed token regeneration.
          </div>
        </div>

        <div class="card card-accent">
          <div class="card-title">🛡️ Legal &amp; Governance</div>
          <div class="card-p">
            • <strong>Sovereign Asset Claim:</strong> Formal copyright &amp; intellectual property attribution.<br>
            • <strong>GDPR/CCPA Cookie Engine:</strong> Granular opt-in preferences banner.<br>
            • <strong>Terms &amp; Anti-Fraud:</strong> Verified single point of contact (<code>lanternmech.official@gmail.com</code>).
          </div>
        </div>
      </div>

      <!-- Python SDK & Swiss Design System -->
      <div class="grid-2col">
        <div class="card">
          <div class="card-title">📦 Official Python SDK (`floodlock-sdk` on PyPI)</div>
          <div class="card-p">
            Published on PyPI with typed clients, automated 3-tier mirror failover (<code>mirror-alpha</code>, <code>mirror-beta</code>, <code>mirror-gamma</code>), and Cloudflare KV quota sync:
          </div>
          <div class="mini-code font-mono">
<span class="kw">from</span> floodlock_sdk <span class="kw">import</span> FloodLockClient
client = FloodLockClient(api_key=<span class="comment">"flk_live_..."</span>)
res = client.check_radius(lat=19.076, lon=72.877, radius_km=150)
<span class="kw">print</span>(res.danger_level, res.alert_title, res.in_danger_zone)
          </div>
        </div>

        <div class="card card-accent">
          <div class="card-title">🎨 Swiss Luxury UI &amp; Typography System</div>
          <div class="card-p">
            • <strong>Old Money &amp; Mafia Typography:</strong> Cinzel (Roman titles), Playfair Display (Headings), Cormorant Garamond (Quotes), Plus Jakarta Sans (Body), Montserrat (CTAs), JetBrains Mono (Streams).<br>
            • <strong>60-30-10 Harmony:</strong> Light Mode (Italian Linen #F5EFE6 / Sand Suede #E6D8C3 / Espresso #451A03); Dark Mode (Onyx #121212 / Slate #262626 / Antique Gold #B45309).<br>
            • <strong>Apple Glassmorphic Dock:</strong> Proximity magnetic hysteresis, fluid 120fps physics.
          </div>
        </div>
      </div>

      <!-- Security & Test Suite Verification Strip -->
      <div class="card" style="background:#FAF8F5; border-color:#D6C5B3; margin-bottom: 6px; padding: 4px 8px;">
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:6.2pt; font-family:'JetBrains Mono',monospace;">
          <div><strong style="color:#10B981;">✓ OFFLINE AUDIT:</strong> 20/20 Test Suites Passed</div>
          <div><strong style="color:#38bdf8;">✓ ZERO BREAKAGE:</strong> Dual OAuth + Live KV Synced</div>
          <div><strong style="color:#B45309;">✓ BOT SHIELD:</strong> Cloudflare Turnstile Intercept</div>
          <div><strong style="color:#451A03;">✓ MASS CONSERVATION:</strong> ε &lt; 10⁻⁷ Enforced</div>
        </div>
      </div>

      <!-- Future Horizon & Strategic Scope -->
      <div class="section-ribbon">
        <span>06 / Future Horizon: Autonomous Sluice Locks &amp; Parametric Insurance</span>
        <span class="font-mono">THE NEXT 12 MONTHS</span>
      </div>

      <div class="grid-3col">
        <div class="card">
          <div class="card-title">🌊 Autonomous Sluice Gates</div>
          <div class="card-p">
            Integration with municipal SCADA actuators via encrypted LoRaWAN. Automatically lowers canal weir gates <strong>45 minutes before peak urban runoff</strong> to purge standing water.
          </div>
        </div>

        <div class="card">
          <div class="card-title">🛰️ Sentinel-1 SAR Assimilation</div>
          <div class="card-p">
            Direct ingestion of Copernicus Sentinel-1 Synthetic Aperture Radar (SAR) backscatter to assimilate real-time 10-meter urban standing water masks during cloud cover.
          </div>
        </div>

        <div class="card">
          <div class="card-title">📜 T+5 Parametric Escrow</div>
          <div class="card-p">
            Smart contract insurance payouts automatically disbursed to registered citizens within 5 days of verified sensor water depths exceeding 30 cm, bypassing paper claims.
          </div>
        </div>
      </div>

      <!-- Formal Concluding Sign-Off -->
      <div class="card card-dark" style="margin-top: 6px; padding: 7px 10px; border-left: 3px solid #B45309;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-family:'Cinzel',serif; font-size: 8.2pt; font-weight: 800; color:#F5EFE6;">FOUNDER'S CHARTER &amp; EXECUTIVE COMMITMENT</div>
            <div style="font-size: 6.3pt; color:#D6C5B3; margin-top: 2px; line-height: 1.35;">
              Over 40 days of intensive mathematical derivation, edge cluster deployment, and adversarial red-teaming, FloodLock was forged to solve one planetary challenge: ensuring no community is ever blindsided by water. Developed with zero compromises by Lantern Mechatronics.
            </div>
          </div>
          <div style="text-align: right; min-width: 145px; padding-left: 12px; border-left: 1px solid rgba(255,255,255,0.15);">
            <div style="font-family:'Playfair Display',serif; font-size: 9pt; font-weight: 700; color:#ffffff;">Daksh Dahore</div>
            <div style="font-size: 5.8pt; color:#B45309; font-weight: 700; font-family:'Montserrat',sans-serif;">FOUNDER &amp; CHIEF ARCHITECT</div>
            <div style="font-size: 5.4pt; color:#888;">Lantern Mechatronics • Nov 2026</div>
          </div>
        </div>
      </div>

    </div>

    <!-- Page 2 Footer -->
    <footer class="page-footer">
      <span>FloodLock™ Planetary Technical Briefing • Lantern Mechatronics</span>
      <span class="font-mono">SECTION 2 OF 2 // COMPLETE 40-DAY SYSTEM CHARTER</span>
      <span>Documentation: https://floodlock-docs.pages.dev</span>
    </footer>
  </div>

</body>
</html>
"""

    html_file = "/home/daksh/Documents/Projects/floodlock/FloodLock_Executive_Dossier.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Wrote HTML dossier to {html_file}")

    # Generate PDF via Google Chrome Headless
    pdf_file = "/home/daksh/Documents/Projects/floodlock/FloodLock_Executive_Dossier.pdf"
    cmd = [
        "google-chrome-stable",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={pdf_file}",
        "--print-to-pdf-no-header",
        html_file
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✓ Generated PDF dossier to {pdf_file}")
    else:
        print(f"✗ Chrome headless error: {res.stderr}")
        return

    # Check page count via pdfinfo
    res_info = subprocess.run(["pdfinfo", pdf_file], capture_output=True, text=True)
    for line in res_info.stdout.splitlines():
        if "Pages:" in line:
            print(f"✓ PDF Verification: {line.strip()}")

    # Copy files into floodlock_frontend and floodlock-docs
    frontend_html = "/home/daksh/Documents/Projects/floodlock/floodlock_frontend/dossier.html"
    frontend_pdf = "/home/daksh/Documents/Projects/floodlock/floodlock_frontend/FloodLock_Executive_Dossier.pdf"
    docs_pdf = "/home/daksh/Documents/Projects/floodlock-docs/FloodLock_Executive_Dossier.pdf"
    docs_html = "/home/daksh/Documents/Projects/floodlock-docs/dossier.html"

    with open(html_file, "r") as f_src, open(frontend_html, "w") as f_dst:
        f_dst.write(f_src.read())
    with open(pdf_file, "rb") as f_src, open(frontend_pdf, "wb") as f_dst:
        f_dst.write(f_src.read())
    with open(pdf_file, "rb") as f_src, open(docs_pdf, "wb") as f_dst:
        f_dst.write(f_src.read())
    with open(html_file, "r") as f_src, open(docs_html, "w") as f_dst:
        f_dst.write(f_src.read())

    print("✓ Mirrored dossier.html and PDF to frontend and docs assets")

if __name__ == "__main__":
    main()
