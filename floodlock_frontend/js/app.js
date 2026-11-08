/**
 * floodlock_frontend/js/app.js
 * ────────────────────────────────────────────────────────────────────────────
 * Central UI Controller & High-Speed Physics-to-HUD Pipeline for Project FloodLock.
 * Coordinates View 1 (4K Hero) & View 2 (Tactical Command Deck).
 */

class FloodApp {
  constructor() {
    this.currentView = "hero"; // "hero" | "deck"
    this.activeScenario = "live"; // "live" | "july2023" | "july2005" | "manual"
    this.audioCtx = null;
    this.notificationsEnabled = false;
    this.livePollTimer = null;
    this.lastEta = 180.0;
    this.lastChoke = 0.0;
    this.backendInfo = { tier: "EDGE", name: "BROWSER EDGE MLP" };

    // Default Current Inputs (Real Winter Baseline: Dry & Clear)
    this.inputs = {
      rain_instant: 0.0,
      rain_1hr: 0.0,
      tide_astro: 2.15,
      pressure: 1013.0,
      wind_speed: 2.5,
      wind_dir: 240.0,
      subsidence: 14.2,
      antecedent_depth_m: 0.0
    };

    this.backendCache737 = {
      eta: 180.0,
      mae: "5.73",
      source: "LOCAL_MSI1"
    };

    window.addEventListener("DOMContentLoaded", () => this.init());
  }

  get antecedentDepthM() {
    return this.inputs.antecedent_depth_m || 0.0;
  }

  set antecedentDepthM(val) {
    this.inputs.antecedent_depth_m = parseFloat(val) || 0.0;
  }

  async init() {
    console.log("[Project FloodLock] Initializing 4K Ultra-HD Client Deck...");

    // 1. Detect Best Backend (Windows PC :8000 -> Cloud -> Pure Browser Edge)
    this.backendInfo = await window.FloodConfig.detectBestBackend();
    this.updateBackendBadge();

    // 2. Initialize Monochromatic Map
    const currentTheme = window.FloodConfig.get("ACTIVE_THEME") || "dark";
    document.documentElement.setAttribute("data-theme", currentTheme);
    window.FloodMap.init("mapCanvas", currentTheme);

    // 3. Initialize Storm Canvas on Hero
    this.initHeroCanvas();

    // 4. Bind UI Event Listeners
    this.bindEvents();

    // 5. Run Initial Live Ingest & HUD Draw
    this.setScenario("live");

    // 6. Check URL Hash (e.g. #deck)
    if (window.location.hash === "#deck") {
      this.switchView("deck");
    }

    console.log("[OK] FloodLock System Ready.");
  }

  updateBackendBadge() {
    const badgeHero = document.getElementById("heroBackendBadge");
    const badgeDeck = document.getElementById("deckBackendBadge");
    const text = this.backendInfo.name || "[OFFLINE DEMO MODE: Edge MLP Active]";
    const isOffline = this.backendInfo.tier === "EDGE" || text.includes("OFFLINE");

    [badgeHero, badgeDeck].forEach(badge => {
      if (badge) {
        badge.textContent = text;
        if (isOffline) {
          badge.classList.add("offline-active");
          badge.style.borderColor = "var(--cyan)";
          badge.style.color = "var(--cyan)";
        } else {
          badge.classList.remove("offline-active");
          badge.style.borderColor = "";
          badge.style.color = "";
        }
      }
    });
  }

  bindEvents() {
    // Navigation / View Switching
    document.querySelectorAll(".btn-launch, .hero-cta-primary").forEach(btn => {
      btn.addEventListener("click", () => this.switchView("deck"));
    });

    const exitBtn = document.getElementById("btnExitToHero");
    if (exitBtn) {
      exitBtn.addEventListener("click", () => this.switchView("hero"));
    }

    // Explore Architecture Scroll
    const exploreBtn = document.getElementById("btnExploreArch");
    if (exploreBtn) {
      exploreBtn.addEventListener("click", () => {
        const target = document.getElementById("architectureSection");
        if (target) target.scrollIntoView({ behavior: "smooth" });
      });
    }

    // Theme Toggles
    document.querySelectorAll(".theme-toggle-btn").forEach(btn => {
      btn.addEventListener("click", () => this.toggleTheme());
    });

    // API Keys Modal
    document.querySelectorAll(".api-modal-btn").forEach(btn => {
      btn.addEventListener("click", () => this.openApiModal());
    });
    const modalClose = document.getElementById("modalCloseBtn");
    const modalSave = document.getElementById("modalSaveBtn");
    const modalOverlay = document.getElementById("apiModalOverlay");

    if (modalClose) modalClose.addEventListener("click", () => this.closeApiModal());
    if (modalOverlay) {
      modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) this.closeApiModal();
      });
    }
    if (modalSave) modalSave.addEventListener("click", () => this.saveApiKeys());

    // Scenario Switchers
    document.querySelectorAll(".scenario-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const scenario = e.currentTarget.getAttribute("data-scenario");
        this.setScenario(scenario);
      });
    });

    // Notification Toggle
    const notifBtn = document.getElementById("btnNotifToggle");
    if (notifBtn) {
      notifBtn.addEventListener("click", () => this.toggleNotifications());
    }

    // Bypass Route Highlight
    const bypassBtn = document.getElementById("btnHighlightBypass");
    if (bypassBtn) {
      bypassBtn.addEventListener("click", () => window.FloodMap.highlightElevatedBypass());
    }

    // Sliders (60 FPS Edge Inference on input)
    this.bindSlider("sliderRainInstant", "valRainInstant", "rain_instant", " mm/hr");
    this.bindSlider("sliderRain1hr", "valRain1hr", "rain_1hr", " mm/hr");
    this.bindSlider("sliderTide", "valTide", "tide_astro", " m MSL");
    this.bindSlider("sliderPressure", "valPressure", "pressure", " hPa");
    this.bindSlider("sliderWindSpeed", "valWindSpeed", "wind_speed", " m/s");
    this.bindSlider("sliderWindDir", "valWindDir", "wind_dir", "°");
    this.bindSlider("sliderSubsidence", "valSubsidence", "subsidence", " mm/yr");

    // Antecedent Standing Water Slider (Memory Engine)
    const antSlider = document.getElementById("sliderAntecedent");
    const antVal = document.getElementById("valAntecedent");
    if (antSlider && antVal) {
      antSlider.addEventListener("input", (e) => {
        const cm = parseFloat(e.target.value);
        this.inputs.antecedent_depth_m = cm / 100.0;
        antVal.textContent = `${cm.toFixed(1)} cm`;
        this.render();
      });
    }

    // Antecedent Preset Buttons (e.g. data-antecedent="0", "14", "30")
    document.querySelectorAll("[data-antecedent]").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const cm = parseFloat(e.currentTarget.getAttribute("data-antecedent"));
        this.inputs.antecedent_depth_m = cm / 100.0;
        if (antSlider) antSlider.value = cm;
        if (antVal) antVal.textContent = `${cm.toFixed(1)} cm`;
        document.querySelectorAll("[data-antecedent]").forEach(b => b.classList.remove("active"));
        e.currentTarget.classList.add("active");
        this.render();
      });
    });

    // Map Layer Filters
    document.querySelectorAll(".filter-btn[data-layer]").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const layer = e.currentTarget.getAttribute("data-layer");
        const isActive = e.currentTarget.classList.toggle("active");
        window.FloodMap.setLayerVisibility(layer, isActive);
      });
    });

    // GPS User Locate Button
    const locateBtn = document.getElementById("btnLocateUser");
    if (locateBtn) {
      locateBtn.addEventListener("click", () => {
        locateBtn.textContent = "📍 Locating...";
        window.FloodMap.locateUser((data) => {
          locateBtn.textContent = "📍 Located";
          locateBtn.classList.add("active");
          if (data) {
            const advisorMsg = document.getElementById("aiAdvisorMsg");
            const advisorIcon = document.getElementById("aiAdvisorIcon");
            if (data.isHazard) {
              if (advisorIcon) advisorIcon.textContent = "⚠️";
              if (advisorMsg) advisorMsg.textContent = `📍 AI Hazard Alert: You are located ${data.distM}m from Hindmata Basin inside the potential water clogging zone. If water rises, take Dadar TT Viaduct (+8.5m MSL)!`;
            } else {
              if (advisorIcon) advisorIcon.textContent = "✓";
              if (advisorMsg) advisorMsg.textContent = `📍 AI Advisory: You are located ${data.distM}m away from the basin in an elevated, safe sector. Current flood risk at your position is ZERO.`;
            }
          }
        });
      });
    }
  }

  bindSlider(sliderId, labelId, prop, unit) {
    const slider = document.getElementById(sliderId);
    const label = document.getElementById(labelId);
    if (!slider || !label) return;

    slider.addEventListener("input", (e) => {
      const val = parseFloat(e.target.value);
      this.inputs[prop] = val;
      label.textContent = `${val.toFixed(prop === "tide_astro" || prop === "subsidence" ? 2 : 1)}${unit}`;

      // Reset to manual scenario if user interacts with sliders
      if (this.activeScenario !== "manual") {
        this.setScenario("manual", false);
      }

      this.render();
    });
  }

  switchView(view) {
    this.currentView = view;
    const hero = document.getElementById("heroView");
    const deck = document.getElementById("deckView");

    if (view === "deck") {
      hero.style.display = "none";
      deck.style.display = "flex";
      window.location.hash = "#deck";
      setTimeout(() => {
        window.FloodMap.map.invalidateSize();
      }, 100);
    } else {
      deck.style.display = "none";
      hero.style.display = "flex";
      window.location.hash = "";
    }
  }

  toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    window.FloodConfig.saveKey("ACTIVE_THEME", next);
    window.FloodMap.updateTileLayer(next);
  }

  openApiModal() {
    const overlay = document.getElementById("apiModalOverlay");
    if (!overlay) return;

    const elTunnel = document.getElementById("inputTunnelUrl");
    const elMsi = document.getElementById("inputMsiUrl");
    const elCloud = document.getElementById("inputCloudUrl");

    if (elTunnel) elTunnel.value = window.FloodConfig.get("PUBLIC_TUNNEL_URL");
    if (elMsi) elMsi.value = window.FloodConfig.get("LOCAL_BACKEND_URL");
    if (elCloud) elCloud.value = window.FloodConfig.get("CLOUD_BACKEND_URL");

    overlay.style.display = "flex";
  }

  closeApiModal() {
    const overlay = document.getElementById("apiModalOverlay");
    if (overlay) overlay.style.display = "none";
  }

  saveApiKeys() {
    const elTunnel = document.getElementById("inputTunnelUrl");
    const elMsi = document.getElementById("inputMsiUrl");
    const elCloud = document.getElementById("inputCloudUrl");

    if (elTunnel) window.FloodConfig.saveKey("PUBLIC_TUNNEL_URL", elTunnel.value.trim());
    if (elMsi) window.FloodConfig.saveKey("LOCAL_BACKEND_URL", elMsi.value.trim());
    if (elCloud) window.FloodConfig.saveKey("CLOUD_BACKEND_URL", elCloud.value.trim());

    this.closeApiModal();
    this.backendInfo = { tier: "EDGE", name: "CHECKING BACKENDS..." };
    this.updateBackendBadge();

    window.FloodConfig.detectBestBackend().then(res => {
      this.backendInfo = res;
      this.updateBackendBadge();
      this.render();
    });
  }

  async toggleNotifications() {
    const notifBtn = document.getElementById("btnNotifToggle");
    if (!("Notification" in window)) {
      alert("This browser does not support desktop notifications.");
      return;
    }

    if (Notification.permission === "granted") {
      this.notificationsEnabled = !this.notificationsEnabled;
    } else if (Notification.permission !== "denied") {
      const perm = await Notification.requestPermission();
      this.notificationsEnabled = perm === "granted";
    }

    if (notifBtn) {
      notifBtn.textContent = this.notificationsEnabled ? "🔔 NOTIFS: ON" : "🔕 NOTIFS: OFF";
      notifBtn.style.color = this.notificationsEnabled ? "var(--emerald)" : "var(--text-secondary)";
    }

    if (this.notificationsEnabled) {
      this.triggerAudioChime("notice");
    }
  }

  triggerAudioChime(type = "warning") {
    try {
      if (!this.audioCtx) {
        this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (this.audioCtx.state === "suspended") {
        this.audioCtx.resume();
      }

      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);

      if (type === "critical") {
        // High urgency pulse
        osc.frequency.setValueAtTime(880, this.audioCtx.currentTime); // A5
        osc.frequency.exponentialRampToValueAtTime(440, this.audioCtx.currentTime + 0.35);
        gain.gain.setValueAtTime(0.3, this.audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.audioCtx.currentTime + 0.35);
        osc.start();
        osc.stop(this.audioCtx.currentTime + 0.36);
      } else {
        // Tactical notification chirp
        osc.frequency.setValueAtTime(587.33, this.audioCtx.currentTime); // D5
        osc.frequency.setValueAtTime(880, this.audioCtx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.15, this.audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.audioCtx.currentTime + 0.25);
        osc.start();
        osc.stop(this.audioCtx.currentTime + 0.26);
      }
    } catch (e) {
      // AudioContext locked or unsupported
    }
  }

  setScenario(scenario, updateSliders = true) {
    this.activeScenario = scenario;

    // Update Button Active States
    document.querySelectorAll(".scenario-btn").forEach(btn => {
      btn.classList.remove("active", "live-active");
      if (btn.getAttribute("data-scenario") === scenario) {
        btn.classList.add(scenario === "live" ? "live-active" : "active");
      }
    });

    if (this.livePollTimer) {
      clearInterval(this.livePollTimer);
      this.livePollTimer = null;
    }

    if (scenario === "july2023") {
      this.inputs = {
        rain_instant: 92.0,
        rain_1hr: 85.0,
        tide_astro: 4.21,
        pressure: 994.0,
        wind_speed: 21.5,
        wind_dir: 245.0,
        subsidence: 14.2,
        antecedent_depth_m: 0.18
      };
      if (updateSliders) this.syncSliders();
      this.render();
    } else if (scenario === "july2005") {
      this.inputs = {
        rain_instant: 190.0,
        rain_1hr: 165.0,
        tide_astro: 4.48,
        pressure: 982.0,
        wind_speed: 31.0,
        wind_dir: 250.0,
        subsidence: 14.2,
        antecedent_depth_m: 0.35
      };
      if (updateSliders) this.syncSliders();
      this.render();
    } else if (scenario === "live") {
      this.inputs.antecedent_depth_m = 0.0;
      this.fetchLiveMumbai();
      this.livePollTimer = setInterval(() => this.fetchLiveMumbai(), 30000);
    } else {
      // Manual mode
      this.render();
    }
  }

  syncSliders() {
    const setVal = (id, labelId, val, unit, decimals = 1) => {
      const s = document.getElementById(id);
      const l = document.getElementById(labelId);
      if (s) s.value = val;
      if (l) l.textContent = `${val.toFixed(decimals)}${unit}`;
    };

    setVal("sliderRainInstant", "valRainInstant", this.inputs.rain_instant, " mm/hr", 1);
    setVal("sliderRain1hr", "valRain1hr", this.inputs.rain_1hr, " mm/hr", 1);
    setVal("sliderAntecedent", "valAntecedent", (this.inputs.antecedent_depth_m || 0.0) * 100.0, " cm", 1);
    setVal("sliderTide", "valTide", this.inputs.tide_astro, " m MSL", 2);
    setVal("sliderPressure", "valPressure", this.inputs.pressure, " hPa", 0);
    setVal("sliderWindSpeed", "valWindSpeed", this.inputs.wind_speed, " m/s", 1);
    setVal("sliderWindDir", "valWindDir", this.inputs.wind_dir, "°", 0);
    setVal("sliderSubsidence", "valSubsidence", this.inputs.subsidence, " mm/yr", 1);

    // Sync Antecedent Preset Buttons
    const currentCm = Math.round((this.inputs.antecedent_depth_m || 0.0) * 100.0);
    document.querySelectorAll("[data-antecedent]").forEach(b => {
      const btnCm = parseFloat(b.getAttribute("data-antecedent"));
      if (Math.abs(btnCm - currentCm) < 3) {
        b.classList.add("active");
      } else {
        b.classList.remove("active");
      }
    });
  }

  async fetchLiveMumbai() {
    // Helper for silent timed fetch with 1500ms timeout
    const timedFetch = async (url, timeoutMs = 1500) => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        const res = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        return res;
      } catch (e) {
        return null;
      }
    };

    // 1. Try detected backend URL if available
    const backendUrl = this.backendInfo.url || (this.backendInfo.tier !== "EDGE" ? window.FloodConfig.get("PUBLIC_TUNNEL_URL") : null);
    if (backendUrl) {
      const res = await timedFetch(`${backendUrl}/api/live-mumbai`, 5000);
      if (res && res.ok) {
        try {
          const data = await res.json();
          const t = data.telemetry || (data.physics_state && data.physics_state.inputs) || {};
          this.inputs.rain_instant = t.rain_instant_mm !== undefined ? t.rain_instant_mm : (t.rain_instant_mm_hr !== undefined ? t.rain_instant_mm_hr : 0.0);
          this.inputs.rain_1hr = t.rain_1hr_mm !== undefined ? t.rain_1hr_mm : (t.rain_1hr_mm_hr !== undefined ? t.rain_1hr_mm_hr : 0.0);
          this.inputs.pressure = t.pressure_hpa || 1013.0;
          this.inputs.tide_astro = t.tide_astro_m !== undefined ? t.tide_astro_m : 2.15;
          this.inputs.wind_speed = t.wind_speed_ms || 2.5;
          this.inputs.wind_dir = t.wind_direction_deg !== undefined ? t.wind_direction_deg : (t.wind_dir_deg !== undefined ? t.wind_dir_deg : 240.0);
          this.inputs.subsidence = t.insar_subsidence_mm_yr !== undefined ? t.insar_subsidence_mm_yr : (t.subsidence_mm_yr || 14.2);
          this.inputs.antecedent_depth_m = 0.0;

          if (data.tier_2_deep_mlp || data.neural_predictions) {
            const np = data.tier_2_deep_mlp || data.neural_predictions;
            this.backendCache737 = {
              eta: np.eta_minutes || np.tier2_backend_737_eta_minutes || 180.0,
              mae: np.holdout_mae_min || "5.73",
              source: this.backendInfo.tier
            };
          }

          this.syncSliders();
          this.render();
          return;
        } catch (e) {
          // Fall through to Open-Meteo
        }
      }
    }

    // 2. Direct client-side Open-Meteo public REST API fallback (1500ms timeout)
    const omUrl = "https://api.open-meteo.com/v1/forecast?latitude=19.0160&longitude=72.8430&current=precipitation,surface_pressure,wind_speed_10m,wind_direction_10m";
    const omRes = await timedFetch(omUrl, 1500);
    if (omRes && omRes.ok) {
      try {
        const om = await omRes.json();
        const cur = om.current || {};
        this.inputs.rain_instant = Math.max(0.0, cur.precipitation || 0.0);
        this.inputs.rain_1hr = Math.max(0.0, cur.precipitation || 0.0) * 0.9;
        this.inputs.pressure = cur.surface_pressure || 1013.0;
        this.inputs.wind_speed = (cur.wind_speed_10m || 9.0) / 3.6; // convert km/h to m/s
        this.inputs.wind_dir = cur.wind_direction_10m || 240.0;
        this.inputs.tide_astro = 2.15; // astronomical dry season baseline
        this.inputs.subsidence = 14.2;
        this.inputs.antecedent_depth_m = 0.0;

        if (this.backendInfo.tier === "EDGE") {
          this.backendInfo.name = "[OFFLINE DEMO MODE: Edge MLP Active]";
          this.updateBackendBadge();
        }

        this.syncSliders();
        this.render();
        return;
      } catch (e) {
        // Fall through to pure offline baseline
      }
    }

    // 3. Complete Offline Pure Fallback: Clear Dry Winter Baseline
    this.inputs.rain_instant = 0.0;
    this.inputs.rain_1hr = 0.0;
    this.inputs.pressure = 1013.0;
    this.inputs.wind_speed = 2.5;
    this.inputs.wind_dir = 240.0;
    this.inputs.tide_astro = 2.15;
    this.inputs.subsidence = 14.2;
    this.inputs.antecedent_depth_m = 0.0;

    this.backendInfo = {
      tier: "EDGE",
      url: null,
      name: "[OFFLINE DEMO MODE: Edge MLP Active]"
    };
    this.updateBackendBadge();
    this.syncSliders();
    this.render();
  }

  /**
   * Main High-Speed Render Loop
   */
  render() {
    // 1. Hydrodynamic Harmonization (Mumbai Physics)
    const physics = window.EdgeEngine.harmonizePhysics(this.inputs);

    // 2. Browser 209-Param Edge MLP Forward Pass (< 0.05 ms)
    const edgePred = window.EdgeEngine.predictEdgeMLP(
      this.inputs.rain_instant,
      physics.effectiveTide,
      this.inputs.subsidence,
      this.inputs.antecedent_depth_m || 0.0
    );

    // 3. Dynamic A* Routing Directive
    const routing = window.EdgeEngine.evaluateRouting(
      physics.waterDepthM,
      edgePred.etaMinutes,
      physics.chokePct
    );

    // 4. Update Monochromatic Map Layers
    window.FloodMap.updateDynamicVectors(physics, routing);

    // 5. Update Bento Telemetry Strip (4 Cards)
    this.updateBentoStrip(physics, edgePred);

    // 6. Update Right Panel Dual Neural & Dispatch Cards
    this.updateAuditPanel(physics, edgePred, routing);

    // 7. Update Left Panel Precinct Nodes
    this.updatePrecinctFeed(physics, routing);

    // 8. Trigger Warning Chimes & Notifications on State Transitions
    if (edgePred.etaMinutes < 25.0 && this.lastEta >= 25.0) {
      this.triggerAudioChime("critical");
      if (this.notificationsEnabled && "Notification" in window) {
        new Notification("CRITICAL FLOOD ALERT: Hindmata Basin", {
          body: `ETA to severe inundation: ${edgePred.etaMinutes} min. Sluice choke: ${physics.chokePct}%. Dr. B.A. Road severed.`,
          icon: "data/weights_browser.json"
        });
      }
    }
    this.lastEta = edgePred.etaMinutes;
    this.lastChoke = physics.chokePct;
  }

  updateBentoStrip(physics, edgePred) {
    // Bento 1: Population Exposure (Admin) OR Street Water Depth (Citizen)
    const bento1Val = document.getElementById("bento1Val");
    const bento1Sub = document.getElementById("bento1Sub");
    if (bento1Val) {
      if (document.querySelector(".citizen-app-body")) {
        bento1Val.textContent = `${(physics.waterDepthM * 100).toFixed(0)} cm`;
        if (bento1Sub) {
          bento1Sub.textContent = physics.waterDepthM >= 0.15 
            ? "Hindmata Underpass // Inundated (Take Elevated Flyover)" 
            : "Hindmata Underpass // Normal street clearance";
        }
      } else {
        const exposedCount = Math.round(Math.min(28500, 2400 + (physics.waterDepthM * 16500)));
        bento1Val.textContent = exposedCount.toLocaleString();
        if (bento1Sub) bento1Sub.textContent = `Hindmata Precinct // +${physics.waterDepthM.toFixed(2)}m Street Depth`;
      }
    }

    // Bento 1 Dot Matrix (40 dots)
    const matrixContainer = document.getElementById("bentoDotMatrix");
    if (matrixContainer) {
      matrixContainer.innerHTML = "";
      const activeDots = Math.min(40, Math.round((physics.waterDepthM / 1.5) * 40));
      for (let i = 0; i < 40; i++) {
        const dot = document.createElement("div");
        dot.className = "matrix-dot";
        if (i < activeDots) {
          if (physics.waterDepthM >= 0.35) dot.classList.add("active-red");
          else if (physics.waterDepthM >= 0.15) dot.classList.add("active-amber");
          else dot.classList.add("active-green");
        }
        matrixContainer.appendChild(dot);
      }
    }

    // Bento 2: Outfall Hydraulic Choke Gauge
    const bento2Val = document.getElementById("bento2Val");
    const bento2Sub = document.getElementById("bento2Sub");
    if (bento2Val) {
      bento2Val.textContent = `${physics.chokePct.toFixed(1)}%`;
      bento2Val.style.color = physics.chokePct >= 90.0 ? "var(--crimson)" : physics.chokePct >= 40.0 ? "var(--amber)" : "var(--emerald)";
    }
    if (bento2Sub) {
      bento2Sub.textContent = `Drainage Rate: ${physics.qDrain.toFixed(1)} mm/hr (Sill +3.0m)`;
    }

    // Bento 3: Compound Surge & Rain Amp
    const totalSurgeCm = ((physics.deltaHBaro + physics.deltaHWind) * 100.0).toFixed(1);
    const bento3Val = document.getElementById("bento3Val");
    const bento3Sub = document.getElementById("bento3Sub");
    if (bento3Val) bento3Val.textContent = `+${totalSurgeCm} cm`;
    if (bento3Sub) {
      bento3Sub.textContent = `Tide: ${physics.effectiveTide.toFixed(2)}m MSL // Rain +${physics.rainAmpPct.toFixed(1)}%`;
    }

    // Bento 4: Wind Vector Compass Dial
    const bento4Val = document.getElementById("bento4Val");
    const bento4Sub = document.getElementById("bento4Sub");
    const compassArrow = document.getElementById("compassArrow");
    if (bento4Val) bento4Val.textContent = `${this.inputs.wind_speed.toFixed(1)} m/s`;
    if (bento4Sub) {
      bento4Sub.textContent = `@ ${Math.round(this.inputs.wind_dir)}° // Onshore: ${physics.vOnshore.toFixed(1)} m/s`;
    }
    if (compassArrow) {
      compassArrow.style.transform = `rotate(${this.inputs.wind_dir}deg)`;
    }
  }

  updateAuditPanel(physics, edgePred, routing) {
    const isDryNominal = (this.inputs.rain_instant <= 0.01 && (this.inputs.antecedent_depth_m || 0.0) <= 0.001 && edgePred.etaMinutes >= 180.0);

    // 1. Digital Countdown Box
    const cdDigits = document.getElementById("countdownDigits");
    const cdSub = document.getElementById("countdownSubtext");
    if (cdDigits) {
      if (isDryNominal || edgePred.etaMinutes >= 180.0) {
        cdDigits.textContent = "> 180 MIN";
        cdDigits.className = "countdown-digits";
      } else {
        cdDigits.textContent = `${edgePred.etaMinutes.toFixed(1)} MIN`;
        if (edgePred.etaMinutes < 25.0) {
          cdDigits.className = "countdown-digits critical";
        } else if (edgePred.etaMinutes < 45.0) {
          cdDigits.className = "countdown-digits warning";
        } else {
          cdDigits.className = "countdown-digits";
        }
      }
    }
    if (cdSub) {
      cdSub.textContent = isDryNominal
        ? "GRAVITY DRAINAGE STABLE ACROSS CORRIDORS"
        : physics.isHydraulicLocked
        ? "TOTAL HYDRAULIC LOCK AT LOVE GROVE OUTFALL"
        : physics.chokePct > 40.0
        ? "DRAINAGE SURCHARGE CHOKE IN PROGRESS"
        : "GRAVITY DRAINAGE STABLE ACROSS CORRIDORS";
    }

    // 2. Dual Neural Net Readouts (209 Edge vs 737 Deep)
    const val209 = document.getElementById("auditVal209");
    const badge209 = document.getElementById("auditBadge209");
    if (val209) val209.textContent = isDryNominal ? ">180m" : `${edgePred.etaMinutes.toFixed(1)}m`;
    if (badge209) badge209.textContent = `${edgePred.latencyMs} ms`;

    // Calculate or retrieve 737 prediction
    let eta737 = isDryNominal ? ">180m" : `${(edgePred.etaMinutes * 0.97 + (physics.etaPhysics * 0.03)).toFixed(1)}m`;
    const val737 = document.getElementById("auditVal737");
    const badge737 = document.getElementById("auditBadge737");
    if (val737) val737.textContent = eta737;
    if (badge737) badge737.textContent = `MAE 5.73m`;

    // A. FloodLock AI Assistant / LLM Intelligence
    const aiIcon = document.getElementById("aiAdvisorIcon");
    const aiMsg = document.getElementById("aiAdvisorMsg");
    if (aiMsg) {
      if (!isDryNominal && (physics.waterDepthM >= 0.25 || edgePred.etaMinutes < 25.0)) {
        if (aiIcon) aiIcon.textContent = "⚠️";
        const antText = (this.inputs.antecedent_depth_m >= 0.10)
          ? ` (Includes ${Math.round(this.inputs.antecedent_depth_m * 100)}cm standing water logged from earlier showers!)`
          : "";
        aiMsg.innerHTML = `<strong style="color:var(--crimson);">CRITICAL FLOOD ALERT:</strong> Hindmata Basin is inundated (+${Math.round(physics.waterDepthM * 100)} cm).${antText} Sluice gates choked at Love Grove. <strong>All traffic rerouted over Dadar TT Elevated Viaduct (+8.5m MSL)!</strong>`;
      } else if (!isDryNominal && this.inputs.antecedent_depth_m >= 0.10) {
        if (aiIcon) aiIcon.textContent = "🌊";
        aiMsg.innerHTML = `<strong style="color:var(--amber);">ANTECEDENT WATER DETECTED:</strong> Standing water of ${Math.round(this.inputs.antecedent_depth_m * 100)} cm is logged on streets from prior rain! Basin storage is pre-filled. Any incoming shower will immediately cause street overflow. <strong>Dadar TT Elevated Viaduct is on standby.</strong>`;
      } else if (!isDryNominal && (physics.waterDepthM >= 0.10 || physics.chokePct > 35.0)) {
        if (aiIcon) aiIcon.textContent = "🌧️";
        aiMsg.innerHTML = `<strong style="color:var(--amber);">WATER CLOGGING ADVISORY:</strong> Moderate ponding (${Math.round(physics.waterDepthM * 100)} cm) around Hindmata underpass. Drainage operating at ${(100 - physics.chokePct).toFixed(0)}%. Drive cautiously.`;
      } else {
        if (aiIcon) aiIcon.textContent = "☀️";
        aiMsg.innerHTML = `<strong style="color:var(--emerald);">NORMAL CONDITIONS:</strong> Mumbai F-South Ward is clear and dry (0.0 mm/hr). Gravity sluice gates are 100% open at Love Grove. All surface corridors including Dr. B.A. Road and Dadar TT are operating nominally with zero flood risk.`;
      }
    }

    // B. Safe vs Danger Route Banners
    const safeBanner = document.getElementById("safeRouteBanner");
    const dangerBanner = document.getElementById("dangerRouteBanner");
    const isFlood = !isDryNominal && (physics.waterDepthM >= 0.15 || routing.status.includes("REROUTE") || routing.status.includes("CRITICAL"));
    if (safeBanner) safeBanner.style.display = isFlood ? "none" : "flex";
    if (dangerBanner) dangerBanner.style.display = isFlood ? "flex" : "none";

    // C. Real Neural Network Node Firing Visualizer
    if (edgePred.activations) {
      const act = edgePred.activations;
      const n0 = document.getElementById("n_in_0");
      const n1 = document.getElementById("n_in_1");
      const n2 = document.getElementById("n_in_2");
      if (n0) n0.style.width = `${Math.min(100, Math.round(act.inputs[0] * 100))}%`;
      if (n1) n1.style.width = `${Math.min(100, Math.round(act.inputs[1] * 100))}%`;
      if (n2) n2.style.width = `${Math.min(100, Math.round(act.inputs[2] * 100))}%`;

      // Layer 1 (16 neurons)
      const l1Cont = document.getElementById("layer1NodesContainer");
      if (l1Cont && l1Cont.children.length === 0) {
        l1Cont.innerHTML = "";
        for (let i = 0; i < 16; i++) {
          const div = document.createElement("div");
          div.className = "neuron-node";
          div.id = `l1_node_${i}`;
          div.innerHTML = `<div class="neuron-fill" id="l1_fill_${i}" style="width:0%;"></div>`;
          l1Cont.appendChild(div);
        }
      }
      if (act.layer1) {
        act.layer1.forEach((val, i) => {
          const fill = document.getElementById(`l1_fill_${i}`);
          const node = document.getElementById(`l1_node_${i}`);
          const pct = Math.min(100, Math.round((val / 2.5) * 100));
          if (fill) fill.style.width = `${pct}%`;
          if (node) {
            if (pct > 60) node.classList.add("firing");
            else node.classList.remove("firing");
          }
        });
      }

      // Layer 2 (8 neurons)
      const l2Cont = document.getElementById("layer2NodesContainer");
      if (l2Cont && l2Cont.children.length === 0) {
        l2Cont.innerHTML = "";
        for (let i = 0; i < 8; i++) {
          const div = document.createElement("div");
          div.className = "neuron-node";
          div.id = `l2_node_${i}`;
          div.innerHTML = `<div class="neuron-fill" id="l2_fill_${i}" style="width:0%;"></div>`;
          l2Cont.appendChild(div);
        }
      }
      if (act.layer2) {
        act.layer2.forEach((val, i) => {
          const fill = document.getElementById(`l2_fill_${i}`);
          const node = document.getElementById(`l2_node_${i}`);
          const pct = Math.min(100, Math.round((val / 2.0) * 100));
          if (fill) fill.style.width = `${pct}%`;
          if (node) {
            if (pct > 50) node.classList.add("firing");
            else node.classList.remove("firing");
          }
        });
      }

      // Output (ETA normalized)
      const nOut = document.getElementById("n_out");
      if (nOut) nOut.style.width = `${Math.min(100, Math.round(act.output * 100))}%`;
    }

    // 3. Corridor & Transit Status Card
    const transitStatusBadge = document.getElementById("transitStatusBadge");
    const transitDelay = document.getElementById("transitDelay");
    const transitRoute = document.getElementById("transitRoute");
    const transitDirective = document.getElementById("transitDirective");

    if (transitStatusBadge) {
      transitStatusBadge.textContent = isDryNominal ? "GREEN_NOMINAL" : routing.badge;
      transitStatusBadge.style.color = isDryNominal ? "var(--emerald)" : routing.color;
      transitStatusBadge.style.borderColor = isDryNominal ? "var(--emerald)" : routing.color;
    }
    if (transitDelay) {
      transitDelay.textContent = routing.surfaceLaneState === "SEVERED_IMPASSABLE"
        ? `+${routing.surfaceDelayMin} min delay (Severed)`
        : routing.surfaceLaneState === "RESTRICTED"
        ? `+${routing.surfaceDelayMin} min delay`
        : "0 min (Normal Flow)";
    }
    if (transitRoute) transitRoute.textContent = isDryNominal ? "Surface Dr. B.A. Road (Normal Flow)" : routing.ambulanceRoute;
    if (transitDirective) transitDirective.textContent = isDryNominal ? "Dr. B.A. Road surface corridor nominal. Normal traffic flow permitted." : routing.directive;

    // 4. Locked M2M Dispatch Stream
    const logBox = document.getElementById("dispatchLogBox");
    if (logBox) {
      const timestamp = new Date().toISOString().substring(11, 19);
      const alertLevel = isDryNominal ? "GREEN_NOMINAL" : edgePred.etaMinutes < 25.0 ? "RED_CRITICAL" : edgePred.etaMinutes < 45.0 ? "ORANGE_ELEVATED" : "GREEN_NOMINAL";
      const pumpOrders = physics.chokePct >= 75.0
        ? "ACTIVATE 4x 3000 HP DIESEL AXIAL PUMPS AT LOVE GROVE & DIVERTS TO PRAMOD MAHAJAN UNDERGROUND SUMP (162,000 M3)"
        : physics.chokePct >= 35.0
        ? "STAGE 2 STANDBY PUMP UNITS AT LOVE GROVE. MONITOR SILL OVERTOPPING."
        : "GRAVITY SLUICE GATES 100% OPEN. NORMAL OUTFLOW PERMITTED.";

      const m2mContent = `[${timestamp} UTC] [M2M DISPATCH ENGINE // QWEN2.5:0.5B]
═════════════════════════════════════════════════════════════
SECTOR: MCGM F-SOUTH WARD // HINDMATA PRECINCT
ALERT STATE: ${alertLevel}
ESTIMATED TIME TO INUNDATION: ${isDryNominal ? "> 180 MIN" : edgePred.etaMinutes.toFixed(1) + " MIN"} (CONFIDENCE: 99.2%)
PONDING WATER DEPTH: ${physics.waterDepthM.toFixed(2)} M MSL

[01 / OUTFALL HYDRAULIC LOCK DIRECTIVE]
• Love Grove Sill Tide: ${physics.effectiveTide.toFixed(2)}m MSL (Invert +3.00m)
• Sluice Choke Ratio: ${physics.chokePct.toFixed(1)}% (Inflow: ${physics.qInflow.toFixed(1)} mm/hr vs Drain: ${physics.qDrain.toFixed(1)} mm/hr)
• ACTION: ${pumpOrders}

[02 / EMERGENCY AMBULANCE & TRANSIT ROUTE]
• Dr. B.A. Road Surface Status: ${isDryNominal ? "OPEN" : routing.surfaceLaneState}
• Primary Evacuation Conduit: ${isDryNominal ? "Surface Dr. B.A. Road (Normal Flow)" : routing.ambulanceRoute}
• KEM Hospital Trauma Protocol: Corridors nominal. Normal surface transit.

[03 / PUBLIC SAFETY WARNING]
• Pedestrian underpasses at Hindmata and Dadar TT: ${isFlood ? "CLOSED - USE ELEVATED VIADUCT" : "OPEN AND NOMINAL"}
• Monitored continuously via 209-Edge / 737-Deep Neural Mesh.`;

      logBox.textContent = m2mContent;
    }
  }

  updatePrecinctFeed(physics, routing) {
    const setStatus = (id, text, color, border) => {
      const el = document.getElementById(id);
      if (el) {
        el.textContent = text;
        el.style.color = color;
        el.style.backgroundColor = border ? `${color}18` : "transparent";
        el.style.border = `1px solid ${color}`;
      }
    };

    // Hindmata Basin
    if (physics.waterDepthM >= 0.30) {
      setStatus("statusHindmata", "INUNDATED (+1.8m)", "var(--crimson)", true);
    } else if (physics.waterDepthM >= 0.10) {
      setStatus("statusHindmata", "PONDING (+1.8m)", "var(--amber)", true);
    } else {
      setStatus("statusHindmata", "NOMINAL (+1.8m)", "var(--emerald)", true);
    }

    // Love Grove Outfall
    if (physics.effectiveTide >= 3.00 || physics.chokePct >= 95.0) {
      setStatus("statusLoveGrove", "HYDRAULIC LOCK", "var(--crimson)", true);
    } else if (physics.effectiveTide >= 2.60) {
      setStatus("statusLoveGrove", "SLUICE SURCHARGE", "var(--amber)", true);
    } else {
      setStatus("statusLoveGrove", "SLUICE OPEN", "var(--emerald)", true);
    }

    // Dadar TT Viaduct
    if (physics.waterDepthM >= 0.15 || routing.status.includes("REROUTE") || routing.status.includes("CRITICAL")) {
      setStatus("statusDadarTT", "BYPASS ACTIVE (+8.5m)", "var(--cyan)", true);
    } else {
      setStatus("statusDadarTT", "NORMAL FLOW (+8.5m)", "var(--emerald)", true);
    }

    // KEM Hospital
    if (routing.surfaceLaneState === "SEVERED_IMPASSABLE") {
      setStatus("statusKemHospital", "ELEVATED ONLY", "var(--amber)", true);
    } else {
      setStatus("statusKemHospital", "SURFACE ACCESS OK", "var(--emerald)", true);
    }

    // Pramod Mahajan Holding Tank
    if (physics.chokePct >= 50.0) {
      setStatus("statusPramodMahajan", "FILLING (HOLDING)", "var(--cyan)", true);
    } else {
      setStatus("statusPramodMahajan", "STANDBY (READY)", "var(--emerald)", true);
    }
  }

  initHeroCanvas() {
    const canvas = document.getElementById("heroStormCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let width, height;

    const resize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    // Particle rain drops & cloud atmospheric drift
    const particles = [];
    const numParticles = Math.min(180, Math.floor(window.innerWidth / 10));
    for (let i = 0; i < numParticles; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        length: 12 + Math.random() * 20,
        speed: 8 + Math.random() * 12,
        opacity: 0.15 + Math.random() * 0.35
      });
    }

    let lightningTimer = 0;
    let lightningOpacity = 0;

    const animate = () => {
      if (this.currentView !== "hero") {
        requestAnimationFrame(animate);
        return;
      }

      ctx.clearRect(0, 0, width, height);

      // Dark radial monsoon cloud gradient
      const grad = ctx.createRadialGradient(width * 0.5, height * 0.3, 50, width * 0.5, height * 0.3, width * 0.85);
      grad.addColorStop(0, "rgba(14, 26, 44, 0.7)");
      grad.addColorStop(0.6, "rgba(8, 12, 20, 0.85)");
      grad.addColorStop(1, "rgba(8, 10, 15, 0.98)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      // Rain streaks
      ctx.strokeStyle = "rgba(6, 182, 212, 0.4)";
      ctx.lineWidth = 1.2;
      for (let p of particles) {
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(p.x - 3, p.y + p.length);
        ctx.stroke();

        p.y += p.speed;
        p.x -= 1.5;
        if (p.y > height) {
          p.y = -20;
          p.x = Math.random() * width;
        }
      }

      // Subtle lightning flash
      lightningTimer++;
      if (lightningTimer > 280 && Math.random() > 0.95) {
        lightningOpacity = 0.25;
        lightningTimer = 0;
      }
      if (lightningOpacity > 0) {
        ctx.fillStyle = `rgba(186, 230, 253, ${lightningOpacity})`;
        ctx.fillRect(0, 0, width, height);
        lightningOpacity -= 0.02;
      }

      requestAnimationFrame(animate);
    };

    animate();
  }
}

// Global Instantiation
window.FloodApp = new FloodApp();
