# /home/daksh/Documents/Projects/floodlock/scripts/make_concise_ui.py
import re

INDEX_PATH = '/home/daksh/Documents/Projects/floodlock/floodlock_frontend/index.html'

with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════════════════════
# 1. COMPACT, HIGH-DENSITY CSS
# ═══════════════════════════════════════════════════════════════════════════
compact_css = """
    /* ── Compact Executive 3-Pillar & Pipeline Styles ── */
    .tri-pillar-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.2rem;
      margin: 2.5rem 0 3.5rem;
    }
    @media (max-width: 900px) {
      .tri-pillar-grid { grid-template-columns: 1fr; }
    }
    .tri-pillar-card {
      background: rgba(10, 15, 26, 0.7);
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: 18px;
      padding: 1.6rem 1.4rem;
      display: flex;
      flex-direction: column;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
      transition: transform 0.2s, border-color 0.2s;
    }
    .tri-pillar-card:hover {
      transform: translateY(-3px);
      border-color: rgba(56, 189, 248, 0.5);
    }
    .tri-pillar-badge {
      font-family: var(--font-mono);
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.25);
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
      width: fit-content;
      margin-bottom: 0.9rem;
    }
    .tri-pillar-title {
      font-family: var(--font-sans);
      font-size: 1.25rem;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.25;
      margin-bottom: 0.75rem;
    }
    .tri-pillar-desc {
      font-size: 0.88rem;
      color: #94a3b8;
      line-height: 1.55;
      margin-bottom: 1rem;
    }
    .tri-pillar-list {
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      padding-top: 0.9rem;
      margin-top: auto;
    }
    .tri-pillar-item {
      font-size: 0.84rem;
      color: #cbd5e1;
      line-height: 1.45;
      display: flex;
      gap: 0.5rem;
    }
    .tri-pillar-item::before {
      content: '▸';
      color: #38bdf8;
      font-weight: 700;
      flex-shrink: 0;
    }
    .tri-pillar-item strong {
      color: #ffffff;
    }

    /* ── Compact 4-Step Pipeline ── */
    .pipeline-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      margin: 2rem 0 3.5rem;
    }
    @media (max-width: 900px) {
      .pipeline-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 600px) {
      .pipeline-grid { grid-template-columns: 1fr; }
    }
    .pipeline-step-card {
      background: rgba(10, 15, 26, 0.65);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 14px;
      padding: 1.25rem 1.1rem;
      transition: all 0.2s ease;
    }
    .pipeline-step-card:hover {
      border-color: rgba(56, 189, 248, 0.4);
      background: rgba(14, 22, 38, 0.8);
    }
    .pipeline-step-num {
      font-family: var(--font-mono);
      font-size: 0.7rem;
      font-weight: 700;
      color: #38bdf8;
      margin-bottom: 0.4rem;
    }
    .pipeline-step-title {
      font-family: var(--font-sans);
      font-size: 1.02rem;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 0.4rem;
    }
    .pipeline-step-desc {
      font-size: 0.82rem;
      color: #94a3b8;
      line-height: 1.5;
    }
    .pipeline-step-badge {
      display: inline-block;
      margin-top: 0.75rem;
      font-family: var(--font-mono);
      font-size: 0.68rem;
      color: #38bdf8;
      background: rgba(56, 189, 248, 0.08);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      border: 1px solid rgba(56, 189, 248, 0.18);
    }

    /* ── Compact Sovereign Leadership Banner ── */
    .sovereign-banner {
      background: linear-gradient(135deg, rgba(13, 19, 32, 0.95) 0%, rgba(6, 10, 18, 0.98) 100%);
      border: 1px solid rgba(56, 189, 248, 0.22);
      border-radius: 20px;
      padding: 2.2rem 2rem;
      margin: 3.5rem 0 3rem;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
    }
"""

# Replace previous injected CSS if present
html = re.sub(r'/\* ── Executive 3-Pillar Architecture \(WHY / WHO / WHEN\) ── \*/[\s\S]*?/\* ── Sovereign Leadership & Institutional Credentials ── \*/[\s\S]*?}\n', '', html)

# Inject compact CSS before </style>
if '.tri-pillar-grid' not in html:
    pos_style = html.find('</style>')
    if pos_style != -1:
        html = html[:pos_style] + compact_css + html[pos_style:]

# ═══════════════════════════════════════════════════════════════════════════
# 2. CONCISE, RAZOR-SHARP VIEW-WELCOME MARKUP
# ═══════════════════════════════════════════════════════════════════════════
concise_view_welcome = """    <!-- ══════════════════════════════════════════════════════════════════
         VIEW 1: WELCOME INTRO — CONCISE, HIGH-IMPACT ENTERPRISE DEFENSE
         ══════════════════════════════════════════════════════════════════ -->
    <section id="view-welcome" class="view-section active">

      <!-- 1. HERO CINEMATIC -->
      <div class="hero-cinematic" style="padding: 4rem 1.5rem 3rem;">
        <div class="hero-badge-pill">
          <span class="pulse-dot-live"></span>
          <span>V8 EDGE RUNTIME • 15 BASINS • 2.7M PARAMETER ENGINE</span>
        </div>

        <h1 class="hero-title-giant" style="margin-bottom: 0.8rem;">
          Planetary Flood Intelligence. <br>
          <span class="gradient-cyan">Sub-Second. Physics-Bounded.</span>
        </h1>

        <p class="hero-subtitle-lead" style="max-width: 680px; margin: 0 auto 2rem; font-size: 1.05rem;">
          Street inundation forecasting at 12ms edge latency with Groq LPU adversarial verification. Eradicating municipal false alarms across global coastal basins.
        </p>

        <div class="hero-cta-group">
          <button class="btn-keynote-primary" onclick="switchView('dashboard')">
            <span>🛰️ Launch Live Tactical Radar</span>
            <span>→</span>
          </button>
          <button class="btn-keynote-secondary" onclick="document.getElementById('executiveMission').scrollIntoView({ behavior: 'smooth' })">
            <span>🏛️ Why / Who / When ↓</span>
          </button>
          <button class="btn-keynote-secondary" onclick="switchView('api')">
            <span>⚡ Developer API Platform</span>
          </button>
        </div>

        <!-- 4-Pillar Compact Metric Strip -->
        <div class="hero-stat-strip" style="margin-top: 2.8rem;">
          <div class="hero-stat-item">
            <div class="hero-stat-num">94.2<span>%</span></div>
            <div class="hero-stat-lbl">Empirical Accuracy</div>
          </div>
          <div class="hero-stat-item">
            <div class="hero-stat-num">12<span>ms</span></div>
            <div class="hero-stat-lbl">Edge Forward Pass</div>
          </div>
          <div class="hero-stat-item">
            <div class="hero-stat-num">2.7<span>M</span></div>
            <div class="hero-stat-lbl">Physics Parameters</div>
          </div>
          <div class="hero-stat-item">
            <div class="hero-stat-num">0<span>.0</span></div>
            <div class="hero-stat-lbl">False Alarms Dispatched</div>
          </div>
        </div>
      </div>

      <!-- 2. CONCISE THREE PILLARS: WHY / WHO / WHEN -->
      <div class="scroll-reveal" id="executiveMission" style="margin: 3.5rem 0 2.5rem;">
        <div class="chapter-eyebrow">EXECUTIVE BRIEFING</div>
        <h2 class="chapter-heading-giant" style="font-size: clamp(1.8rem, 3.5vw, 2.6rem); margin-bottom: 0.5rem;">
          Why MeteoFlood. Who It Protects. When It Operates.
        </h2>
        <p class="chapter-lead-text" style="font-size: 0.96rem; margin-bottom: 1.5rem;">
          Explaining the core operational mission in three concise architectural pillars:
        </p>

        <div class="tri-pillar-grid">

          <!-- PILLAR I: WHY -->
          <div class="tri-pillar-card">
            <div class="tri-pillar-badge">WHY USE METEOFLOOD</div>
            <h3 class="tri-pillar-title">Eliminating the 6-Hour Lag &amp; 74% False Alarm Tax</h3>
            <p class="tri-pillar-desc">
              Conventional systems (HEC-RAS, LISFLOOD) take 6–14 hours on supercomputers. By then, underpasses are drowned. Concurrently, 74% of municipal sirens are false alarms from crude rainfall gauges that ignore soil absorption, wasting $12M+ per storm in transit shutdowns.
            </p>
            <div class="tri-pillar-list">
              <div class="tri-pillar-item"><span><strong>12ms Edge Pass:</strong> Solves shallow water physics at CDN edge instead of 6-hour supercomputers.</span></div>
              <div class="tri-pillar-item"><span><strong>1.4s Groq Audit:</strong> Adversarial LPU checks soil headroom to suppress false alarms before sirens fire.</span></div>
            </div>
          </div>

          <!-- PILLAR II: WHO -->
          <div class="tri-pillar-card">
            <div class="tri-pillar-badge">WHO USES METEOFLOOD</div>
            <h3 class="tri-pillar-title">Civil Defense &amp; Critical Arterial Operators</h3>
            <p class="tri-pillar-desc">
              Built for operators where missing flood depths means loss of life or catastrophic infrastructure failure:
            </p>
            <div class="tri-pillar-list">
              <div class="tri-pillar-item"><span><strong>Disaster Command (NDMA, FEMA):</strong> Automated evacuation triggers &amp; safe egress corridors.</span></div>
              <div class="tri-pillar-item"><span><strong>Transit &amp; Rail Grids:</strong> Real-time trackbed &amp; underpass floodgate closure.</span></div>
              <div class="tri-pillar-item"><span><strong>Port Authorities:</strong> Estuarine tidal surge backflow capping at municipal outfalls.</span></div>
              <div class="tri-pillar-item"><span><strong>Supply Chains &amp; Fleets:</strong> Dynamic route clearance for emergency logistics.</span></div>
            </div>
          </div>

          <!-- PILLAR III: WHEN -->
          <div class="tri-pillar-card">
            <div class="tri-pillar-badge">WHEN TO USE METEOFLOOD</div>
            <h3 class="tri-pillar-title">The 4-Stage Operational Timeline</h3>
            <p class="tri-pillar-desc">
              Continuous intelligence operating throughout the lifecycle of extreme hydrometeorological events:
            </p>
            <div class="tri-pillar-list">
              <div class="tri-pillar-item"><span><strong>T - 30 to 7 Days:</strong> Pre-monsoon soil moisture (θ) &amp; aquifer (SPI-90) calibration.</span></div>
              <div class="tri-pillar-item"><span><strong>T - 48 to 12 Hours:</strong> Convective cloudburst tracking via CAPE &amp; NASA IMERG radar.</span></div>
              <div class="tri-pillar-item"><span><strong>T - 3 Hours to T - 0:</strong> Sub-second street depth forward passes at distributed edge.</span></div>
              <div class="tri-pillar-item"><span><strong>Post-Storm:</strong> Forensic peak crest audit &amp; drainage capacity restitution logs.</span></div>
            </div>
          </div>

        </div>
      </div>

      <!-- 3. HOW IT WORKS: 4-STEP PIPELINE -->
      <div class="scroll-reveal" style="margin: 3.5rem 0 2.5rem;">
        <div class="chapter-eyebrow">HOW IT WORKS</div>
        <h2 class="chapter-heading-giant" style="font-size: clamp(1.8rem, 3.5vw, 2.6rem); margin-bottom: 0.5rem;">
          4-Tier Autonomous Intelligence Pipeline
        </h2>
        <p class="chapter-lead-text" style="font-size: 0.96rem; margin-bottom: 1.5rem;">
          From 18 planetary satellite streams to verified sub-second civil defense with zero human latency:
        </p>

        <div class="pipeline-grid">
          <div class="pipeline-step-card">
            <div class="pipeline-step-num">00 // INGEST</div>
            <div class="pipeline-step-title">Multi-Modal Planetary Mesh</div>
            <div class="pipeline-step-desc">
              Continuously ingests Copernicus GloFAS 90d discharge, NASA GPM radar, NOAA GFS/HRRR 3km grids, and WorldTides oceanic backpressure.
            </div>
            <div class="pipeline-step-badge">18 DATA STREAMS</div>
          </div>

          <div class="pipeline-step-card">
            <div class="pipeline-step-num">01 // COMPUTE</div>
            <div class="pipeline-step-title">2.7M PINN Edge Core</div>
            <div class="pipeline-step-desc">
              Proprietary physics neural surrogate compiled to WebAssembly &amp; V8 edge isolates. Evaluates 14 vectors in 12ms under strict mass-conservation.
            </div>
            <div class="pipeline-step-badge">12ms FORWARD PASS</div>
          </div>

          <div class="pipeline-step-card">
            <div class="pipeline-step-num">02 // VERIFY</div>
            <div class="pipeline-step-title">Groq LPU Adversarial Gate</div>
            <div class="pipeline-step-desc">
              Tier-1 Groq LPU (openai/gpt-oss-120b) cross-checks predictions against soil absorption &amp; coastal tides in 1.4s, suppressing false sirens.
            </div>
            <div class="pipeline-step-badge">1.4s CAUSAL AUDIT</div>
          </div>

          <div class="pipeline-step-card">
            <div class="pipeline-step-num">03 // DISPATCH</div>
            <div class="pipeline-step-title">Autonomous Infrastructure</div>
            <div class="pipeline-step-desc">
              Dispatches authenticated emergency webhooks, evacuation routing, and SDK telemetry directly to municipal SCADA centers globally.
            </div>
            <div class="pipeline-step-badge">SUB-15ms WEBHOOKS</div>
          </div>
        </div>
      </div>

      <!-- 4. ACT I: THE HYDROLOGICAL CRISIS (INTERACTIVE SPLIT SLIDER) -->
      <div class="scroll-reveal" style="margin: 3.5rem 0 2.5rem;">
        <div class="chapter-eyebrow">ACT I // LATENCY COMPARISON</div>
        <h2 class="chapter-heading-giant" style="font-size: clamp(1.8rem, 3.5vw, 2.6rem); margin-bottom: 0.5rem;">
          6-Hour Supercomputer Blindspot vs. 12ms Edge Physics
        </h2>
        <p class="chapter-lead-text" style="font-size: 0.96rem; margin-bottom: 1.5rem;">
          Drag the slider to compare conventional central modeling against MeteoFlood edge surrogate:
        </p>

        <!-- Interactive Split-Slider -->
        <div class="split-slider-box" id="splitSliderBox">
          <!-- Left Layer -->
          <div class="split-layer split-left" id="splitLeftLayer">
            <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #ef4444; background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; padding: 0.25rem 0.7rem; border-radius: 999px; width: fit-content; margin-bottom: 0.6rem; font-weight: 700;">
              ❌ CONVENTIONAL MODELING
            </span>
            <h3 style="font-size: 1.5rem; color: #ffffff; margin-bottom: 0.4rem; font-weight: 700;">6-Hour Latency Blindspot</h3>
            <p style="font-size: 0.88rem; color: #fca5a5; max-width: 400px; line-height: 1.5;">
              Central grid solves miss micro-cloudbursts. Sirens fire 40 minutes AFTER streets drown, or trigger false alarms on dry soil.
            </p>
            <div style="font-family: var(--font-mono); font-size: 0.78rem; color: #f87171; margin-top: 1rem;">
              • Delay: <strong>360+ Min</strong> • False Alarms: <strong>48.6%</strong>
            </div>
          </div>

          <!-- Right Layer -->
          <div class="split-layer split-right">
            <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #38bdf8; background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; padding: 0.25rem 0.7rem; border-radius: 999px; width: fit-content; margin-bottom: 0.6rem; font-weight: 700;">
              ✓ METEOFLOOD 2.7M EDGE PINN
            </span>
            <h3 style="font-size: 1.5rem; color: #ffffff; margin-bottom: 0.4rem; font-weight: 700;">12ms Real-Time Street Physics</h3>
            <p style="font-size: 0.88rem; color: #93c5fd; max-width: 400px; line-height: 1.5;">
              Soil saturation, tidal capping, and 2D shallow water dynamics solved in a single edge tensor pass at nearest CDN node.
            </p>
            <div style="font-family: var(--font-mono); font-size: 0.78rem; color: #38bdf8; margin-top: 1rem;">
              • Latency: <strong>0.012 Seconds</strong> • Accuracy: <strong>94.2%</strong>
            </div>
          </div>

          <div class="split-handle" id="splitHandle">⟷</div>
        </div>
      </div>

      <!-- 5. ACT II: 14-FEATURE PROPRIETARY TENSOR ATTRIBUTION -->
      <div class="scroll-reveal" style="margin: 3.5rem 0 2.5rem;">
        <div class="chapter-eyebrow">ACT II // PROPRIETARY TENSOR ATTRIBUTION</div>
        <h2 class="chapter-heading-giant" style="font-size: clamp(1.8rem, 3.5vw, 2.6rem); margin-bottom: 0.5rem;">
          14 Physical Vectors. Mass-Conserved to Machine Epsilon.
        </h2>
        <p class="chapter-lead-text" style="font-size: 0.96rem; margin-bottom: 1.5rem;">
          MeteoFlood bounds every neural prediction to physical mass conservation. Click any vector to inspect its operational role:
        </p>

        <!-- 14-Feature Interactive Tensor Matrix -->
        <div class="tensor-matrix-grid" id="tensorMatrixContainer">
          <div class="tensor-chip active" onclick="inspectTensorFeature(0)">
            <div class="tensor-chip-index">VECTOR [00]</div>
            <div class="tensor-chip-name">Rainfall Intensity R₀</div>
            <div class="tensor-chip-physics">mm/hr Doppler rate</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(1)">
            <div class="tensor-chip-index">VECTOR [01]</div>
            <div class="tensor-chip-name">Antecedent Load R₄₈</div>
            <div class="tensor-chip-physics">48h Cumulative rain</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(2)">
            <div class="tensor-chip-index">VECTOR [02]</div>
            <div class="tensor-chip-name">Subsurface Memory R₁₂₀</div>
            <div class="tensor-chip-physics">120h Basin storage</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(3)">
            <div class="tensor-chip-index">VECTOR [03]</div>
            <div class="tensor-chip-name">Convective CAPE</div>
            <div class="tensor-chip-physics">J/kg Cloudburst energy</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(4)">
            <div class="tensor-chip-index">VECTOR [04]</div>
            <div class="tensor-chip-name">Pressure Drop ΔP</div>
            <div class="tensor-chip-physics">hPa Barometric surge</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(5)">
            <div class="tensor-chip-index">VECTOR [05]</div>
            <div class="tensor-chip-name">Surface Wind Drag</div>
            <div class="tensor-chip-physics">km/h 10m storm sheer</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(6)">
            <div class="tensor-chip-index">VECTOR [06]</div>
            <div class="tensor-chip-name">SPI-30 Drought Index</div>
            <div class="tensor-chip-physics">Moisture baseline</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(7)">
            <div class="tensor-chip-index">VECTOR [07]</div>
            <div class="tensor-chip-name">SPI-90 Deep Aquifer</div>
            <div class="tensor-chip-physics">Groundwater head</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(8)">
            <div class="tensor-chip-index">VECTOR [08]</div>
            <div class="tensor-chip-name">Volumetric Soil θ</div>
            <div class="tensor-chip-physics">Non-linear saturation</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(9)">
            <div class="tensor-chip-index">VECTOR [09]</div>
            <div class="tensor-chip-name">Hydraulic Infiltration Kₛ</div>
            <div class="tensor-chip-physics">mm/hr Soil permeability</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(10)">
            <div class="tensor-chip-index">VECTOR [10]</div>
            <div class="tensor-chip-name">Drainage Proximity</div>
            <div class="tensor-chip-physics">Canal outfall distance</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(11)">
            <div class="tensor-chip-index">VECTOR [11]</div>
            <div class="tensor-chip-name">Topographic TWI</div>
            <div class="tensor-chip-physics">Micro-terrain sink</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(12)">
            <div class="tensor-chip-index">VECTOR [12]</div>
            <div class="tensor-chip-name">Urban Imperviousness</div>
            <div class="tensor-chip-physics">Asphalt concrete fraction</div>
          </div>
          <div class="tensor-chip" onclick="inspectTensorFeature(13)">
            <div class="tensor-chip-index">VECTOR [13]</div>
            <div class="tensor-chip-name">Tidal Surge H_tide</div>
            <div class="tensor-chip-physics">Coastal head backpressure</div>
          </div>
        </div>

        <!-- Dynamic Specification Card -->
        <div class="card-luxury" id="tensorEquationBox" style="background: rgba(8, 12, 22, 0.9); border-color: rgba(56, 189, 248, 0.35); padding: 1.6rem;">
          <div style="font-family: var(--font-mono); font-size: 0.74rem; color: #38bdf8; margin-bottom: 0.3rem;" id="formulaVectorTitle">
            [VECTOR 00 // PRECIPITATION FLUX R₀]
          </div>
          <div style="font-family: var(--font-mono); font-size: 0.96rem; color: #ffffff; margin-bottom: 0.4rem; font-weight: 600;" id="formulaSpec">
            Real-Time Dual-Polarization Doppler Radar &amp; NASA GPM IMERG Microwave Array
          </div>
          <p style="font-size: 0.88rem; color: #94a3b8; line-height: 1.55;" id="formulaExplanation">
            1-minute precipitation flux bounded by non-Euclidean spatial convolution to prevent rainfall velocity discontinuities.
          </p>
        </div>
      </div>

      <!-- 6. ACT III: ADVERSARIAL GROQ LPU TESTBENCH -->
      <div class="scroll-reveal" style="margin: 3.5rem 0 2.5rem;">
        <div class="chapter-eyebrow">ACT III // ZERO FALSE PANIC</div>
        <h2 class="chapter-heading-giant" style="font-size: clamp(1.8rem, 3.5vw, 2.6rem); margin-bottom: 0.5rem;">
          Adversarial Groq LPU Verification Gate
        </h2>
        <p class="chapter-lead-text" style="font-size: 0.96rem; margin-bottom: 1.5rem;">
          Groq LPU cross-examines neural predictions against physical soil headroom in 1.4 seconds before alerts sound:
        </p>

        <!-- Live Interactive Groq Testbench -->
        <div class="groq-testbench-card" style="padding: 1.6rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.8rem; margin-bottom: 1.2rem;">
            <div>
              <span style="font-family: var(--font-mono); font-size: 0.72rem; color: #38bdf8; font-weight: 700;">ENGINE: Tier-1 Groq LPU (openai/gpt-oss-120b)</span>
              <h3 style="font-size: 1.3rem; color: #ffffff; margin-top: 0.15rem; font-weight: 700;">Simulate Verification</h3>
            </div>
            <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
              <button class="btn-water" onclick="simulateGroqTestbench('monsoon')" style="font-size: 0.82rem; padding: 0.5rem 1.1rem;">
                🚨 Monsoon Surge
              </button>
              <button class="btn-keynote-secondary" onclick="simulateGroqTestbench('dry_false_alarm')" style="font-size: 0.82rem; padding: 0.5rem 1.1rem;">
                🛡️ Dry False Alarm
              </button>
            </div>
          </div>

          <!-- 3-Stage Pipeline Flow -->
          <div class="testbench-stage-flow" style="margin-bottom: 1.2rem;">
            <div class="stage-card">
              <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #94a3b8;">STAGE 01</div>
              <div style="font-weight: 700; color: #ffffff; font-size: 0.96rem;">Neural Edge Pass</div>
              <div style="font-size: 0.76rem; color: #38bdf8; margin-top: 0.2rem;" id="tbStage1Status">14-F Prediction: +28.4 cm</div>
            </div>
            <div class="stage-arrow">→</div>
            <div class="stage-card" style="border-color: rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.05);">
              <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #38bdf8;">STAGE 02</div>
              <div style="font-weight: 700; color: #ffffff; font-size: 0.96rem;">Groq LPU Audit</div>
              <div style="font-size: 0.76rem; color: #6ee7b7; margin-top: 0.2rem;" id="tbStage2Status">Cross-Checking Physics...</div>
            </div>
            <div class="stage-arrow">→</div>
            <div class="stage-card" id="tbStage3Card" style="border-color: #10b981; background: rgba(16, 185, 129, 0.08);">
              <div style="font-family: var(--font-mono); font-size: 0.68rem; color: #10b981;">STAGE 03</div>
              <div style="font-weight: 700; color: #10b981; font-size: 0.96rem;" id="tbVerdictBadge">✓ FALSE ALARM DISMISSED</div>
              <div style="font-size: 0.76rem; color: #94a3b8; margin-top: 0.2rem;" id="tbActionBadge">Alert Suppressed</div>
            </div>
          </div>

          <!-- Console Live Telemetry Log -->
          <div style="background: #050810; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 1.1rem; font-family: var(--font-mono); font-size: 0.82rem; color: #a5f3fc; line-height: 1.55;" id="tbConsoleOutput">
            [GROQ AUDIT VERDICT]: SUB_HAZARD_WATCH_ADVISORY • Confidence: 94/100<br>
            [PHYSICAL AUDIT]: Zero rain (R₀ = 0.0), 55% soil saturation, and 0.08m tide leave ample capacity. Forecast refuted as false positive.<br>
            [TACTICAL ADVISORY]: Conditions nominal. Transit routes operating without restriction.
          </div>
        </div>
      </div>

      <!-- 7. ACT IV: DEVELOPER SDK TERMINAL -->
      <div class="scroll-reveal" style="margin: 3.5rem 0 2.5rem;">
        <div class="chapter-eyebrow">DEVELOPER SDK</div>
        <h2 class="chapter-heading-giant" style="font-size: clamp(1.8rem, 3.5vw, 2.6rem); margin-bottom: 0.5rem;">
          Query Edge Telemetry in 2 Lines of Code
        </h2>
        <p class="chapter-lead-text" style="font-size: 0.96rem; margin-bottom: 1.5rem;">
          Published Python package (<code>pip install floodlock-sdk</code>), cURL REST API, and TypeScript bindings:
        </p>

        <!-- Code Terminal Deck -->
        <div class="code-terminal-deck" style="margin: 1.5rem 0;">
          <div class="code-terminal-tabs">
            <button class="code-tab-btn active" onclick="switchCodeTab('python')">Python SDK (floodlock-sdk)</button>
            <button class="code-tab-btn" onclick="switchCodeTab('curl')">cURL REST API</button>
            <button class="code-tab-btn" onclick="switchCodeTab('ts')">TypeScript / Node</button>
            <div style="margin-left: auto; display: flex; gap: 0.5rem; align-items: center;">
              <button onclick="runCodeSnippetDemo()" class="btn-water" style="padding: 0.3rem 0.75rem; font-size: 0.74rem;">▶ Run Edge Query</button>
              <button onclick="copyCurrentCodeSnippet()" class="btn-keynote-secondary" style="padding: 0.3rem 0.75rem; font-size: 0.74rem;" id="copyCodeBtn">📋 Copy</button>
            </div>
          </div>

          <pre class="code-terminal-body" id="codeTerminalDisplay" style="padding: 1.4rem; font-size: 0.86rem;"><code>from floodlock_sdk import FloodLockClient

client = FloodLockClient(api_key="flk_live_...")
result = client.check_radius(lat=19.21, lon=73.10, radius_km=150)

print(result.danger_level)     # PERIMETER_NOMINAL
print(result.in_danger_zone)   # False
print(result.threat_verified)  # False (Suppressed)</code></pre>
        </div>
      </div>

      <!-- 8. SOVEREIGN LEADERSHIP & PILOT BRIEFING -->
      <div class="sovereign-banner scroll-reveal">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.5rem;">
          <div style="max-width: 620px;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.8rem;">
              <img src="assets/logo.jpg" alt="Lantern Mechatronics" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 2px solid #38bdf8;">
              <div>
                <div style="font-family: var(--font-sans); font-size: 1.15rem; font-weight: 700; color: #ffffff;">Daksh Dahore</div>
                <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #38bdf8;">FOUNDER &amp; CHIEF SYSTEMS ARCHITECT • LANTERN MECHATRONICS</div>
              </div>
            </div>
            <p style="font-size: 0.92rem; color: #94a3b8; line-height: 1.6; margin: 0;">
              MeteoFlood is engineered as sovereign planetary infrastructure for disaster command authorities, metropolitan transit networks, and critical utilities worldwide.
            </p>
          </div>
          <div style="display: flex; flex-direction: column; gap: 0.6rem; min-width: 240px;">
            <a href="mailto:contact@lanternmechatronics.com" class="btn-keynote-primary" style="justify-content: center; text-decoration: none; padding: 0.65rem 1.2rem; font-size: 0.86rem;">
              <span>Institutional Pilot Briefing →</span>
            </a>
            <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #64748b; text-align: center;">
              contact@lanternmechatronics.com
            </div>
          </div>
        </div>
      </div>

    </section>
"""

# Replace HTML view-welcome
pos1_html = html.find('<!-- ══════════════════════════════════════════════════════════════════\n         VIEW 1: WELCOME INTRO')
pos2_html = html.find('<!-- ══════════════════════════════════════════════════════════════════\n         VIEW 2: PASSWORDLESS AUTH')

if pos1_html != -1 and pos2_html != -1:
    html = html[:pos1_html] + concise_view_welcome + html[pos2_html:]
    print("Concise HTML replaced successfully!")
else:
    print("ERROR finding HTML markers:", pos1_html, pos2_html)

# ═══════════════════════════════════════════════════════════════════════════
# 3. TIGHTEN JAVASCRIPT TENSOR_SPEC (1-LINERS)
# ═══════════════════════════════════════════════════════════════════════════
concise_tensor_spec = """    // ── 14-Feature Tensor Specification Inspector (Proprietary - Zero Reverse-Engineering) ──
    const TENSOR_SPEC = [
      {
        title: "[VECTOR 00 // PRECIPITATION FLUX R₀]",
        spec: "Real-Time Dual-Polarization Doppler Radar & NASA GPM IMERG Microwave Array",
        desc: "1-minute rainfall rate bounded by non-Euclidean spatial convolution to prevent overland velocity spikes."
      },
      {
        title: "[VECTOR 01 // 48-HOUR ANTECEDENT LOAD]",
        spec: "48-Hour Rolling Spatial Inundation Buffer",
        desc: "Tracks root-zone pre-saturation, routing excess storm rain directly to surface sheet flow."
      },
      {
        title: "[VECTOR 02 // 120-HOUR CATCHMENT MEMORY]",
        spec: "5-Day Catchment Budget & Evapotranspiration Reanalysis",
        desc: "Quantifies deep valley saturation across the watershed, preventing false security during multi-day storms."
      },
      {
        title: "[VECTOR 03 // CONVECTIVE CAPE INSTABILITY]",
        spec: "NOAA High-Resolution Rapid Refresh (HRRR) 3km Field",
        desc: "Measures vertical atmospheric buoyancy to pre-activate edge passes before cloudbursts breach radar."
      },
      {
        title: "[VECTOR 04 // BAROMETRIC CYCLONE DROP ΔP]",
        spec: "Micro-Barometric Station Mesh & NOAA Cyclonic Feeds",
        desc: "Ingests inverted-barometer sea dome elevation, forecasting coastal surge before landfall."
      },
      {
        title: "[VECTOR 05 // SURFACE WIND DRAG VECTOR]",
        spec: "10-Meter Coastal Anemometers & Marine Wind Profilers",
        desc: "Calculates onshore wind drag blocking gravity stormwater egress through urban canal mouths."
      },
      {
        title: "[VECTOR 06 // STANDARDIZED MOISTURE SPI-30]",
        spec: "30-Day Satellite Precipitation Anomaly Feeds",
        desc: "Distinguishes hydrophobic dry-baked runoff regimes from permeable soil conditions."
      },
      {
        title: "[VECTOR 07 // DEEP AQUIFER HEAD SPI-90]",
        spec: "Multi-Month Groundwater Network & Gravimetric Altimetry",
        desc: "Monitors subterranean aquifer capacity to absorb extreme precipitation without surface pooling."
      },
      {
        title: "[VECTOR 08 // VOLUMETRIC SOIL SATURATION θ]",
        spec: "Microwave Soil Moisture Radiometry & In-Situ Sensors",
        desc: "Non-linear absorption barrier. Below threshold, rain absorbs underground and suppresses sirens."
      },
      {
        title: "[VECTOR 09 // SUBTERRANEAN CONDUCTIVITY Kₛ]",
        spec: "Geotechnical Lithology & Soil Porosity Mapping",
        desc: "Encodes spatial substrate permeability, governing maximum downward filtration velocity."
      },
      {
        title: "[VECTOR 10 // OUTFALL TOPOLOGICAL PROXIMITY]",
        spec: "Vectorized Drainage Basin Graph & Municipal Canal Net",
        desc: "Measures non-Euclidean concentration times to arterial underpasses and urban choke points."
      },
      {
        title: "[VECTOR 11 // TOPOGRAPHIC SINK INDEX TWI]",
        spec: "1-Meter LiDAR Digital Elevation Models & Slope Gradients",
        desc: "Pinpoints micro-topographic runoff convergence zones where street flooding pools first."
      },
      {
        title: "[VECTOR 12 // URBAN IMPERVIOUS SURFACE FRACTION]",
        spec: "Multi-Spectral Land-Cover Satellite Classification",
        desc: "Zeroes infiltration across asphalt/concrete grids for immediate kinetic runoff computation."
      },
      {
        title: "[VECTOR 13 // ESTUARINE TIDAL SURGE H_TIDE]",
        spec: "Coastal Acoustic Radar Buoys & Astronomical Tide Gauges",
        desc: "Identifies when high ocean tides lock gravity outfalls, forcing stormwater backward into streets."
      }
    ];"""

pos_spec1 = html.find('    // ── 14-Feature Tensor Specification Inspector')
pos_spec2 = html.find('    function inspectTensorFeature(idx) {')

if pos_spec1 != -1 and pos_spec2 != -1:
    html = html[:pos_spec1] + concise_tensor_spec + '\n\n' + html[pos_spec2:]
    print("Concise TENSOR_SPEC replaced successfully!")
else:
    print("WARNING: Could not find TENSOR_SPEC markers:", pos_spec1, pos_spec2)

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("Concise transformation complete!")

