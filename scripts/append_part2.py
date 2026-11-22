# scripts/append_part2.py
part2 = """
  <!-- ══════════════════════════════════════════════════════════════════
       WATERY FLUID SIDEBAR (DYNAMIC DOCK)
       ══════════════════════════════════════════════════════════════════ -->
  <aside class="water-sidebar" id="waterSidebar">
    <!-- Pre-Login Items -->
    <div id="dockPreLogin" style="display: flex; flex-direction: column; gap: 0.6rem; width: 100%;">
      <div class="water-dock-item active" onclick="switchView('welcome')">
        <span class="dock-icon">🌊</span>
        <span class="dock-label">Intro Story</span>
      </div>
      <div class="water-dock-item" onclick="switchView('auth')">
        <span class="dock-icon">🔐</span>
        <span class="dock-label">Login Gate</span>
      </div>
      <div class="water-dock-item" onclick="switchView('opensource')">
        <span class="dock-icon">📦</span>
        <span class="dock-label">Open Source</span>
      </div>
    </div>

    <!-- Post-Login Items -->
    <div id="dockPostLogin" style="display: none; flex-direction: column; gap: 0.6rem; width: 100%;">
      <div class="water-dock-item" onclick="switchView('dashboard')">
        <span class="dock-icon">🛰️</span>
        <span class="dock-label">Tactical Map</span>
      </div>
      <div class="water-dock-item" onclick="switchView('api')">
        <span class="dock-icon">⚡</span>
        <span class="dock-label">API Platform</span>
      </div>
      <div class="water-dock-item" onclick="switchView('account')">
        <span class="dock-icon">👤</span>
        <span class="dock-label">My Account</span>
      </div>
      <div class="water-dock-item" onclick="switchView('opensource')">
        <span class="dock-icon">📦</span>
        <span class="dock-label">Open Source</span>
      </div>
      <div class="water-dock-item" onclick="switchView('contact')">
        <span class="dock-icon">🔬</span>
        <span class="dock-label">Contribute</span>
      </div>
      <div class="water-dock-item" onclick="switchView('settings')">
        <span class="dock-icon">⚙️</span>
        <span class="dock-label">Settings</span>
      </div>
    </div>
  </aside>

  <!-- ══════════════════════════════════════════════════════════════════
       TOP HEADER & BANNER
       ══════════════════════════════════════════════════════════════════ -->
  <header>
    <a href="#" class="brand" onclick="switchView('welcome')">Flood<span>Lock</span></a>
    <div class="header-actions">
      <button id="adminHeaderBtn" onclick="openAdminModal()" style="display: flex; padding: 0.45rem 0.95rem; font-size: 0.8rem; border-radius: 999px; background: rgba(181, 107, 54, 0.35); border: 1px solid var(--c-cognac-hover); color: var(--c-linen); cursor: pointer; align-items: center; gap: 0.4rem; font-family: var(--font-sans); font-weight: 600; transition: all 0.2s;">
        <span>👑 Founder Admin</span>
        <span id="headerPendingBadge" style="background: #ef4444; color: #fff; font-size: 0.65rem; padding: 0.15rem 0.45rem; border-radius: 999px; font-weight: 700; display: none;">0</span>
      </button>

      <button onclick="openCommercialInquiryModal()" style="padding: 0.45rem 0.95rem; font-size: 0.8rem; border-radius: 999px; background: rgba(6, 182, 212, 0.2); border: 1px solid #06b6d4; color: #E2F1F8; cursor: pointer; display: flex; align-items: center; gap: 0.4rem; font-weight: 600;">
        <span>💼 Commercial License</span>
      </button>

      <div class="status-badge">
        <span class="status-dot"></span>
        <span id="headerEngineStatus">GloFAS Telemetry Active</span>
      </div>

      <div id="headerAuthBtnContainer">
        <button onclick="switchView('auth')" class="btn-water" style="padding: 0.4rem 1.1rem; font-size: 0.85rem;">Login / Register</button>
      </div>
    </div>
  </header>

  <!-- ══════════════════════════════════════════════════════════════════
       MAIN CONTENT WRAPPER
       ══════════════════════════════════════════════════════════════════ -->
  <main class="main-wrapper">

    <!-- ══════════════════════════════════════════════════════════════════
         VIEW 1: WELCOME INTRO — 4K SCROLL STORYTELLING
         ══════════════════════════════════════════════════════════════════ -->
    <section id="view-welcome" class="view-section active">
      <div class="story-hero-header">
        <div style="font-family: var(--font-mono); font-size: 0.8rem; letter-spacing: 0.18em; text-transform: uppercase; color: #38bdf8; margin-bottom: 0.75rem;">
          Compound Planetary Hydrology • 12ms Edge Surrogate
        </div>
        <h1>FLOOD<em>LOCK</em></h1>
        <p style="font-size: 1.25rem; color: var(--c-text-muted); max-width: 720px; margin: 0 auto 1.5rem; font-weight: 300;">
          A multi-tier neural framework forecasting flash floods, convective cloudbursts, and tidal outfall backflow with sub-minute precision.
        </p>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
          <button class="btn-magnetic" onclick="switchView('auth')">
            <span>Enter Tactical Gateway</span>
            <span>→</span>
          </button>
          <button class="btn-water" onclick="document.getElementById('storyCanvasContainer').scrollIntoView({ behavior: 'smooth' })">
            <span>Scroll Down to Reveal Narrative ↓</span>
          </button>
        </div>
      </div>

      <!-- 4K Interactive Storytelling Canvas -->
      <div class="story-canvas-container" id="storyCanvasContainer">
        <canvas id="storyCanvas"></canvas>
        <div class="story-hud-overlay">
          <div class="story-hud-box" id="storyHudBox">
            <div class="story-hud-tag" id="storyHudTag">
              <span>🌧️</span> <span>SCENE 1 // SERENE JAPANESE TOWN</span>
            </div>
            <div class="story-hud-title" id="storyHudTitle">What is FloodLock?</div>
            <div class="story-hud-desc" id="storyHudDesc">
              Water droplets slide off traditional tile roofs, splashing against the letters. FloodLock is an edge-native compound flood intelligence platform coupling Saint-Venant shallow water equations with sub-second neural inference across 15 global river basins.
            </div>
          </div>
          <div class="story-timeline-scrubber">
            <span style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8;">STORY SCRUBBER:</span>
            <input type="range" id="storyScrubber" min="0" max="100" value="10" style="width: 130px; accent-color: #38bdf8;">
            <button onclick="toggleAudioFx()" id="audioToggleBtn" style="background:none; border:none; color:var(--c-linen); cursor:pointer; font-size:1.1rem;" title="Toggle Ambient Water Sounds">🔊</button>
          </div>
        </div>
      </div>

      <!-- Narrative Scenes Breakdown Grid -->
      <div class="scene-block">
        <div class="card-luxury">
          <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8; margin-bottom: 0.5rem;">SCENE 2 // THE CONCRETE JUNGLE</div>
          <h2 style="font-family: var(--font-display); font-size: 2.2rem; margin-bottom: 0.75rem;">What are urban floods?</h2>
          <p style="color: var(--c-text-muted); font-size: 0.98rem; margin-bottom: 1.25rem;">
            When extreme convective precipitation collides with impervious asphalt grids and locked gravity outfalls, water has nowhere to soak. Arterial roads turn into 2-meter deep raging canals in under 20 minutes.
          </p>
          <div style="padding: 1rem; border-radius: 12px; background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.25); font-size: 0.85rem; color: #a5f3fc;">
            💡 <em>Interactive: Drag your mouse over the canvas above to create hydrodynamic ripples with real-time synthesized water sounds!</em>
          </div>
        </div>

        <div class="card-luxury">
          <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #ef4444; margin-bottom: 0.5rem;">SCENE 3 // THE CRISIS AT SEA</div>
          <h2 style="font-family: var(--font-display); font-size: 2.2rem; margin-bottom: 0.75rem;">Submerged cars &amp; the broken plank</h2>
          <p style="color: var(--c-text-muted); font-size: 0.98rem; margin-bottom: 1.25rem;">
            Cars bob helplessly in the swirling inundation. A struggling survivor clutches a wooden plank—suddenly, floating debris strikes! The wood snaps, and the survivor slips into the deep.
          </p>
          <p style="color: var(--c-beige); font-size: 0.92rem; border-left: 3px solid #ef4444; padding-left: 0.85rem;">
            As you scroll down to search for the survivor, text locks onto the vortex: traditional municipal warnings update every 6 hours. When seconds decide life or death, FloodLock computes 36-step street depths in <strong>12 milliseconds</strong>. Scroll up, and the survivor safely drifts to safety!
          </p>
        </div>
      </div>

      <!-- Scene 4: Water Drains Away & Math De-scrambler -->
      <div class="card-luxury" style="margin: 3.5rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #34d399;">SCENE 4 // HYDRODYNAMIC RESTORATION</div>
            <h2 style="font-family: var(--font-display); font-size: 2.4rem;">How does FloodLock solve this?</h2>
          </div>
          <button class="btn-water" onclick="triggerMathDescramble()">
            <span>⚡ Re-Scramble Physics Equations</span>
          </button>
        </div>

        <div class="math-descrambler-box">
          <div style="font-size: 0.75rem; color: #7dd3fc; margin-bottom: 0.75rem; letter-spacing: 0.1em;">
            [V8 TENSOR KERNEL: SIMPLIFYING NON-LINEAR SHALLOW WATER PDES]
          </div>
          <div class="math-scramble-text" id="mathScrambleText">
            ∂h/∂t + ∇·(hu) = R - I(t) ⟷ Capping: H_tide - Z_invert ⟷ MSE: 3.96cm ⟷ Torricelli Outfall
          </div>
        </div>
        <p style="color: var(--c-text-muted); font-size: 0.95rem; margin-top: 1.25rem;">
          By compressing 14-hour supercomputer computational fluid dynamics into an ultra-low latency 14-feature neural surrogate, FloodLock delivers millisecond-level street flood depths directly to citizens and civil authorities.
        </p>
      </div>

      <!-- Scene 5: Data Sources with Google-Style Search -->
      <div class="card-luxury" style="margin: 3.5rem 0;">
        <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8;">SCENE 5 // CONTINUOUS TELEMETRY</div>
        <h2 style="font-family: var(--font-display); font-size: 2.2rem; margin-bottom: 0.5rem;">Information Sources Explorer</h2>
        <p style="color: var(--c-text-muted); font-size: 0.95rem;">
          Search or click any official planetary telemetry stream ingested into FloodLock's multi-cloud mesh.
        </p>

        <div class="sources-search-bar">
          <span style="font-size: 1.2rem;">🔍</span>
          <input type="text" id="sourcesSearchInput" placeholder="Search data feeds (e.g. Copernicus GloFAS, NOAA, ECMWF, JMA)...">
          <button onclick="alert('Viewing 18 Integrated Atmospheric Feeds')" class="btn-water" style="padding: 0.35rem 0.85rem; font-size: 0.78rem;">View All 18 Feeds</button>
        </div>

        <div class="sources-chips" id="sourcesChipsContainer">
          <span class="source-chip">🌊 ECMWF Copernicus GloFAS (90-Day Gridded Discharge)</span>
          <span class="source-chip">🛰️ NOAA GFS &amp; HRRR (Atmospheric Pressure &amp; CAPE)</span>
          <span class="source-chip">🌧️ NASA GPM IMERG (Satellite Precipitation Radar)</span>
          <span class="source-chip">🌀 JMA Typhoon Track &amp; Coastal Radar</span>
          <span class="source-chip">📊 Open-Meteo Planetary Hydrology API</span>
          <span class="source-chip">🌊 WorldTides &amp; Copernicus Marine (Astronomical Surge)</span>
        </div>
      </div>

      <!-- Scene 6: Why Custom AI & Blistering 150 Token/Sec Stream -->
      <div class="scene-block">
        <div class="card-luxury">
          <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #f59e0b;">SCENE 6 // EDGE SURROGATE</div>
          <h2 style="font-family: var(--font-display); font-size: 2.2rem; margin-bottom: 0.75rem;">Why custom AI here?</h2>
          <p style="color: var(--c-text-muted); font-size: 0.95rem; margin-bottom: 1.25rem;">
            Standard general-purpose LLMs hallucinate physics and fail basic conservation laws. FloodLock's custom 14-feature surrogate is mathematically constrained by Green-Ampt infiltration and Torricelli submerged orifice capping, guaranteeing mass residuals &lt; 10⁻¹⁴ m.
          </p>
          <button class="btn-water" onclick="startTokenStreamDemo()">
            <span>▶️ Run 150 Token/s Inference Stream</span>
          </button>
        </div>

        <div class="token-stream-terminal" id="tokenStreamTerminal">
          <div style="color: #64748b; font-size: 0.75rem; margin-bottom: 0.5rem;">[EDGE SURROGATE STREAMING // TIER 1 GROQ LPU &amp; V8 ISOLATE]</div>
          <span id="tokenStreamOutput">Click 'Run 150 Token/s Inference Stream' to witness edge speed...</span>
          <span class="token-cursor"></span>
        </div>
      </div>

      <!-- Scene 7: Why Choose Us, Instagram-Style DMs & Trashed Feedback -->
      <div class="scene-block" style="margin: 3.5rem 0;">
        <div>
          <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #a855f7;">SCENE 7 // COMMUNITY REVIEWS</div>
          <h2 style="font-family: var(--font-display); font-size: 2.2rem; margin-bottom: 0.75rem;">Why choose FloodLock?</h2>
          <p style="color: var(--c-text-muted); font-size: 0.95rem; margin-bottom: 1.25rem;">
            See why hydrologists, disaster responders, and port authorities across 15 global river basins rely on FloodLock's zero-fake alert guarantee.
          </p>
          <div style="padding: 1rem; border-radius: 14px; background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.3); font-size: 0.88rem; color: #e9d5ff;">
            💬 Have thoughts? Send feedback below. Our automated recycling engine disposes of it with zero corporate bureaucracy!
          </div>
        </div>

        <div class="insta-dm-deck">
          <div class="insta-dm-header">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span style="font-size: 1.2rem;">📬</span>
              <strong style="font-size: 0.95rem;">Hydrology Dispatch Inbox</strong>
            </div>
            <span class="insta-unread-badge">100+ New Messages</span>
          </div>

          <div class="insta-dm-body" id="instaDmBody">
            <div class="dm-bubble">
              <strong>@social_media_user_1</strong>
              Did your radar detect the Rhine River cloudburst before municipal civil defense sirens?
              <div style="color:#38bdf8; margin-top:0.3rem;">↳ FloodLock: Yes, alert dispatched 18 minutes prior to municipal sirens.</div>
            </div>
            <div class="dm-bubble">
              <strong>@tokyo_civil_engineer</strong>
              Is hydrostatic equilibrium strictly enforced at coastal tidal outfalls?
              <div style="color:#38bdf8; margin-top:0.3rem;">↳ FloodLock: Bounded by Torricelli backwater capping (Htide - Zinvert).</div>
            </div>
            <div class="dm-bubble">
              <strong>@valencia_delta_monitor</strong>
              Are citizen sensor reports accepted blindly or verified?
              <div style="color:#38bdf8; margin-top:0.3rem;">↳ FloodLock: Secondary belief protocol verifies terrain elevation and radar contours before training ingestion.</div>
            </div>
          </div>

          <div class="dm-input-area" id="dmInputArea">
            <input type="text" id="userFeedbackInput" placeholder="Type your feedback (e.g. Needs more river gauges)...">
            <button onclick="sendAndTrashFeedback()" class="btn-water" style="padding: 0.5rem 1rem; font-size: 0.85rem;">Send</button>
            <div class="trash-bin-visual" id="trashBinIcon" title="Zero-Bureaucracy Feedback Shredder">🗑️</div>
          </div>
        </div>
      </div>

      <!-- Scene 8: About Founder (Hacker Terminal Style) -->
      <div class="founder-code-terminal">
        <pre><code>print("════════════════════════════════════════════════════════════════")
print("FOUNDER & CHIEF ARCHITECT: Daksh Dahore (Age: 14)")
print("ORGANIZATION: LanternMech / FloodLock Planetary Initiative")
print("MISSION: Zero-Latency Physics-Informed Hydrology")
print("CORE PLATFORM: 14-Feature V8 Surrogate + ECMWF Copernicus GloFAS")
print("ETHOS: Zero Fake Alerts • Absolute Mass Conservation")
print("════════════════════════════════════════════════════════════════")</code></pre>
      </div>
    </section>
"""

with open("/home/daksh/Projects/floodlock/floodlock_frontend/index.html", "a", encoding="utf-8") as f:
    f.write(part2)
print("Part 2 appended")
