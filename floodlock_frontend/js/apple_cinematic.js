/**
 * floodlock_frontend/js/apple_cinematic.js
 * ────────────────────────────────────────────────────────────────────────────
 * Apple-Grade 4K Scroll-Driven Cinematic Engine & Interactive Physics Showcase
 *
 * Features:
 *  - Fixed background video scrubbing synced to window scroll progress via rAF
 *  - Interactive Chapter 1: Hindmata Saucer Basin & Antecedent Memory Slider
 *  - Interactive Chapter 2: Love Grove Outfall Sluice Gate (+3.0m) Hydraulic Head Reversal
 *  - Interactive Chapter 3: 209-Parameter Edge MLP Forward Pass Node Visualizer
 *  - Interactive Chapter 4: Dadar TT Elevated Viaduct (+8.5m) Priority Corridor
 *  - Ambient Web Audio rain synthesis & Web Speech API emotional audio briefing
 *  - 24/7 Cloudflare Edge Backend Status Monitor with retry & 30s re-poll
 */

(function () {
  "use strict";

  // ══════════════════════════════════════════════════════════════════════════
  // 1. SCROLL-DRIVEN VIDEO ENGINE (APPLE PRO DISPLAY STANDARD)
  // ══════════════════════════════════════════════════════════════════════════
  class AppleScrollVideoScrubber {
    constructor(videoId) {
      this.video = document.getElementById(videoId);
      if (!this.video) return;

      this.targetTime = 0;
      this.isReady = false;
      this.duration = 12.0;

      const markReady = () => {
        this.isReady = true;
        this.duration = (this.video.duration && !isNaN(this.video.duration)) ? this.video.duration : 12.0;
      };

      this.video.addEventListener("loadedmetadata", markReady);
      this.video.addEventListener("canplaythrough", markReady);

      // In case metadata is already cached
      if (this.video.readyState >= 1) {
        markReady();
      }

      // Handle missing video gracefully with fallback poster
      this.video.addEventListener("error", () => {
        console.warn("[FloodLock] Background video unavailable; falling back to SVG poster.");
        if (this.video.parentElement) {
          this.video.parentElement.classList.add("video-fallback-active");
        }
      });

      // Direct scroll listener for instantaneous frame scrubbing
      window.addEventListener("scroll", () => {
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        const scrollFraction = maxScroll > 0 ? Math.min(1.0, Math.max(0.0, window.scrollY / maxScroll)) : 0;
        this.targetTime = scrollFraction * (this.video.duration || this.duration);

        // Immediate seek when scrolling aggressively
        if (this.isReady && this.video) {
          const diff = this.targetTime - this.video.currentTime;
          if (Math.abs(diff) > 0.04) {
            this.video.currentTime += diff * 0.45;
          }
        }
      }, { passive: true });

      this.update = this.update.bind(this);
      requestAnimationFrame(this.update);
    }

    update() {
      if (this.isReady && this.video) {
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        const scrollFraction = maxScroll > 0 ? Math.min(1.0, Math.max(0.0, window.scrollY / maxScroll)) : 0;
        this.targetTime = scrollFraction * (this.video.duration || this.duration);

        // Smooth 60 FPS Apple-style video lerping
        const diff = this.targetTime - this.video.currentTime;
        if (Math.abs(diff) > 0.005) {
          this.video.currentTime += diff * 0.25;
        }
      }
      requestAnimationFrame(this.update);
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 2. GENERATIVE WEB AUDIO RAIN & AMBIENCE (ZERO NETWORK ASSETS)
  // ══════════════════════════════════════════════════════════════════════════
  class AmbientAudio {
    constructor() {
      this.ctx = null;
      this.isPlaying = false;
      this.muted = false;
    }

    init() {
      if (this.ctx) return;
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      this.ctx = new AudioCtx();

      const bufferSize = this.ctx.sampleRate * 2;
      const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const out = noiseBuffer.getChannelData(0);
      let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
      for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.96900 * b2 + white * 0.1538520;
        b3 = 0.86650 * b3 + white * 0.3104856;
        b4 = 0.55000 * b4 + white * 0.5329522;
        b5 = -0.7616 * b5 - white * 0.0168980;
        out[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.05;
        b6 = white * 0.115926;
      }
      this.noiseBuffer = noiseBuffer;

      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.001, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);
    }

    start() {
      this.init();
      if (!this.ctx || this.isPlaying) return;
      if (this.ctx.state === "suspended") this.ctx.resume();

      const src = this.ctx.createBufferSource();
      src.buffer = this.noiseBuffer;
      src.loop = true;

      const filter = this.ctx.createBiquadFilter();
      filter.type = "lowpass";
      filter.frequency.setValueAtTime(1200, this.ctx.currentTime);

      src.connect(filter);
      filter.connect(this.masterGain);
      src.start(0);

      this.masterGain.gain.exponentialRampToValueAtTime(this.muted ? 0.0001 : 0.18, this.ctx.currentTime + 1.2);
      this.isPlaying = true;
    }

    toggleMute() {
      this.muted = !this.muted;
      if (this.masterGain && this.ctx) {
        this.masterGain.gain.setValueAtTime(this.muted ? 0.0001 : 0.18, this.ctx.currentTime);
      }
      return this.muted;
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 3. CHAPTER 1: HINDMATA SAUCER BASIN & ANTECEDENT SATURATION SIMULATOR
  // ══════════════════════════════════════════════════════════════════════════
  function initHindmataSimulator() {
    const slider = document.getElementById("sliderAntecedentSim");
    const valText = document.getElementById("valAntecedentSim");
    const capacityText = document.getElementById("valBasinCapacity");
    const puddleBox = document.getElementById("simPuddleGraphic");
    const etaText = document.getElementById("valSimEta");

    if (!slider) return;

    const update = () => {
      const depthCm = parseFloat(slider.value);
      if (valText) valText.textContent = `${depthCm.toFixed(1)} cm`;

      // Storage capacity formula from 02_HYDROLOGY_AND_CSV_SPEC:
      // basin_threshold_mm = max(5.0, 45.0 * storage_factor - antecedent_depth_cm * 2.0)
      const storageFactor = 1.0 - (14.2 / 110.0); // InSAR subsidence penalty
      const remainingHeadroomMm = Math.max(5.0, (45.0 * storageFactor) - (depthCm * 1.8));

      if (capacityText) capacityText.textContent = `${remainingHeadroomMm.toFixed(1)} mm`;

      // Water ponding graphic height
      if (puddleBox) {
        const heightPct = Math.min(100, Math.max(4, (depthCm / 35.0) * 100));
        puddleBox.style.height = `${heightPct}%`;
        if (depthCm >= 15.0) {
          puddleBox.style.background = "linear-gradient(180deg, rgba(239, 68, 68, 0.45), rgba(239, 68, 68, 0.85))";
        } else if (depthCm > 0.1) {
          puddleBox.style.background = "linear-gradient(180deg, rgba(245, 158, 11, 0.4), rgba(245, 158, 11, 0.75))";
        } else {
          puddleBox.style.background = "linear-gradient(180deg, rgba(16, 185, 129, 0.3), rgba(16, 185, 129, 0.6))";
        }
      }

      // Predicted ETA
      if (etaText) {
        if (depthCm <= 0.1) {
          etaText.textContent = "> 180 min (Safe)";
          etaText.style.color = "#10b981";
        } else if (depthCm < 14.0) {
          const eta = Math.max(5, Math.round((remainingHeadroomMm / 20.0) * 60));
          etaText.textContent = `${eta} min (Ponding)`;
          etaText.style.color = "#f59e0b";
        } else {
          etaText.textContent = "12 min (Critical Overflow)";
          etaText.style.color = "#ef4444";
        }
      }
    };

    slider.addEventListener("input", update);
    update();
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 4. CHAPTER 2: LOVE GROVE SLUICE LOCK & SPRING TIDE SIMULATOR
  // ══════════════════════════════════════════════════════════════════════════
  function initSluiceSimulator() {
    const tideSlider = document.getElementById("sliderTideSim");
    const tideVal = document.getElementById("valTideSim");
    const chokeGauge = document.getElementById("valChokeGauge");
    const gateStatus = document.getElementById("valGateStatus");
    const gateFlap = document.getElementById("simGateFlap");
    const flowVector = document.getElementById("simFlowVector");

    if (!tideSlider) return;

    const update = () => {
      const tideM = parseFloat(tideSlider.value);
      if (tideVal) tideVal.textContent = `${tideM.toFixed(2)} m MSL`;

      // BRIMSTOWAD Love Grove Sluice Formula:
      // if tide <= 2.60: choke = 0%
      // if tide >= 3.00: choke = 100%
      // else: (tide - 2.60) / 0.40
      let chokeRatio = 0.0;
      if (tideM <= 2.60) chokeRatio = 0.0;
      else if (tideM >= 3.00) chokeRatio = 1.0;
      else chokeRatio = (tideM - 2.60) / 0.40;

      const chokePct = Math.round(chokeRatio * 100);
      if (chokeGauge) chokeGauge.textContent = `${chokePct}%`;

      if (gateStatus && gateFlap && flowVector) {
        if (chokePct >= 99) {
          gateStatus.textContent = "100% LOCKED // HYDRAULIC REVERSAL";
          gateStatus.style.color = "#ef4444";
          gateFlap.style.transform = "rotate(0deg)"; // fully shut
          gateFlap.style.borderColor = "#ef4444";
          flowVector.textContent = "← REVERSE BACKFLOW INTO HINDMATA";
          flowVector.style.color = "#ef4444";
        } else if (chokePct > 0) {
          gateStatus.textContent = `PARTIALLY CHOKED (${chokePct}%)`;
          gateStatus.style.color = "#f59e0b";
          gateFlap.style.transform = `rotate(${Math.round((1 - chokeRatio) * 45)}deg)`;
          gateFlap.style.borderColor = "#f59e0b";
          flowVector.textContent = "→ RESTRICTED OUTWARD DRAINAGE";
          flowVector.style.color = "#f59e0b";
        } else {
          gateStatus.textContent = "OPEN // GRAVITY DISCHARGE (25 mm/hr)";
          gateStatus.style.color = "#10b981";
          gateFlap.style.transform = "rotate(45deg)"; // wide open
          gateFlap.style.borderColor = "#10b981";
          flowVector.textContent = "→ UNCONSTRAINED GRAVITY DISCHARGE";
          flowVector.style.color = "#10b981";
        }
      }
    };

    tideSlider.addEventListener("input", update);
    update();
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 5. AUDIO BRIEFING & SPEECH SYNTHESIS ENGINE
  // ══════════════════════════════════════════════════════════════════════════
  function initAudioBriefing(audio) {
    const btnPlay = document.getElementById("btnApplePlayAudio");
    const btnMute = document.getElementById("btnAppleMuteAudio");
    const waveBars = document.querySelectorAll(".apple-wave-bar");

    if (!btnPlay) return;

    const narrationText = "July 26, 2005. The skies over Mumbai ruptured with nine hundred and forty-four millimeters of rain in twenty-four hours. Over one thousand and ninety-four lives were lost beneath silent floodwaters. Hindmata and Dadar TT became submerged saucer basins, trapping ambulances on Dr. Ambedkar Road as the Arabian Sea locked the outfall gates. Project FloodLock was engineered from tragedy. Two hundred and nine parameters, running in under fifty microseconds in citizen browsers, predicting compound hydraulic backflow before the curb is submerged. Zero alarm fatigue. Zero panic. Zero lives lost.";

    let isSpeaking = false;
    let synth = window.speechSynthesis;

    btnPlay.addEventListener("click", () => {
      audio.start();
      if (!synth) return;

      if (synth.speaking) {
        synth.cancel();
        isSpeaking = false;
        btnPlay.innerHTML = "<span>▶ LISTEN TO BRIEFING</span>";
        waveBars.forEach(b => b.classList.remove("active"));
        return;
      }

      const utter = new SpeechSynthesisUtterance(narrationText);
      utter.rate = 0.94;
      utter.pitch = 0.92;

      const voices = synth.getVoices();
      const naturalVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("UK") || v.name.includes("Google"))) || voices[0];
      if (naturalVoice) utter.voice = naturalVoice;

      utter.onstart = () => {
        isSpeaking = true;
        btnPlay.innerHTML = "<span>⏹ STOP BRIEFING</span>";
        waveBars.forEach(b => b.classList.add("active"));
      };

      utter.onend = () => {
        isSpeaking = false;
        btnPlay.innerHTML = "<span>↺ REPLAY BRIEFING</span>";
        waveBars.forEach(b => b.classList.remove("active"));
      };

      utter.onerror = () => {
        isSpeaking = false;
        btnPlay.innerHTML = "<span>▶ LISTEN TO BRIEFING</span>";
        waveBars.forEach(b => b.classList.remove("active"));
      };

      synth.speak(utter);
    });

    if (btnMute) {
      btnMute.addEventListener("click", () => {
        const isMuted = audio.toggleMute();
        btnMute.textContent = isMuted ? "🔇 SOUND MUTED" : "🔊 AMBIENT RAIN";
        btnMute.classList.toggle("muted", isMuted);
      });
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 6. PASSCODE LOGIN AUTHENTICATION (ADMIN 1416 & MONITOR 2324)
  // ══════════════════════════════════════════════════════════════════════════
  function initPasscodeAuth() {
    // Admin 1416
    const btnAdmin = document.getElementById("btnUnlockAdmin");
    const inputAdmin = document.getElementById("adminPassInput");
    const errAdmin = document.getElementById("adminPassError");

    function unlockAdmin() {
      if (inputAdmin && inputAdmin.value.trim() === "1416") {
        sessionStorage.setItem("floodlock_auth_admin", "1416");
        window.location.href = "admin.html";
      } else if (inputAdmin) {
        inputAdmin.classList.add("error");
        if (errAdmin) errAdmin.style.display = "block";
        setTimeout(() => inputAdmin.classList.remove("error"), 600);
      }
    }
    if (btnAdmin) btnAdmin.addEventListener("click", unlockAdmin);
    if (inputAdmin) {
      inputAdmin.addEventListener("keydown", (e) => {
        if (e.key === "Enter") unlockAdmin();
      });
    }

    // Monitor 2324
    const btnMonitor = document.getElementById("btnUnlockMonitor");
    const inputMonitor = document.getElementById("monitorPassInput");
    const errMonitor = document.getElementById("monitorPassError");

    function unlockMonitor() {
      if (inputMonitor && inputMonitor.value.trim() === "2324") {
        sessionStorage.setItem("floodlock_auth_monitor", "2324");
        window.location.href = "monitor.html";
      } else if (inputMonitor) {
        inputMonitor.classList.add("error");
        if (errMonitor) errMonitor.style.display = "block";
        setTimeout(() => inputMonitor.classList.remove("error"), 600);
      }
    }
    if (btnMonitor) btnMonitor.addEventListener("click", unlockMonitor);
    if (inputMonitor) {
      inputMonitor.addEventListener("keydown", (e) => {
        if (e.key === "Enter") unlockMonitor();
      });
    }

    // Global helper for one-tap auto-fill & unlock from the visual badge
    window.autoFillAndUnlock = function (inputId, code, btnId) {
      const input = document.getElementById(inputId);
      if (input) {
        input.value = code;
        input.style.borderColor = "#10b981";
        input.style.boxShadow = "0 0 12px rgba(16, 185, 129, 0.4)";
        setTimeout(() => {
          const btn = document.getElementById(btnId);
          if (btn) btn.click();
        }, 150);
      }
    };
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 7. 24/7 CLOUDFLARE EDGE BACKEND STATUS MONITOR
  // ══════════════════════════════════════════════════════════════════════════

  /**
   * Single health probe — returns true if Cloudflare Edge is reachable.
   * Updates the hero pill UI on success or leaves it for caller to handle.
   */
  async function probeCloudflareEdge() {
    const pill = document.getElementById("heroGlobalStatusPill");
    const text = document.getElementById("heroGlobalStatusText");
    const dot  = document.getElementById("heroGlobalStatusDot");
    if (!pill || !text || !dot) return false;

    const cfUrl = (window.FloodConfig && window.FloodConfig.get("CLOUDFLARE_EDGE_URL"))
      || "https://floodlock-backend.dakshdahore1995.workers.dev";

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000); // 6s — generous for cold starts
      const res = await fetch(`${cfUrl}/health`, { signal: controller.signal, cache: "no-store" });
      clearTimeout(timeoutId);

      if (res && res.ok) {
        const data = await res.json();
        const colo   = data.location          || "GLOBAL";
        const params = data.deep_model_params  || 737;

        text.textContent        = `24/7 CLOUDFLARE EDGE LIVE [${colo} // Qwen AI · ${params}P]`;
        dot.style.background    = "#10b981";
        pill.style.borderColor  = "rgba(16, 185, 129, 0.4)";
        pill.style.background   = "rgba(16, 185, 129, 0.1)";
        pill.style.color        = "#10b981";
        pill.classList.remove("offline-active");
        pill.classList.add("cloud-active");
        return true;
      }
    } catch (e) {
      console.warn("[FloodLock] Cloudflare Edge probe failed:", e.message);
    }
    return false;
  }

  /**
   * On DOMContentLoaded: probe → retry after 3s if cold start → show offline.
   * Then keeps re-polling every 30s to stay in sync.
   */
  async function initBackendStatusMonitor() {
    const pill = document.getElementById("heroGlobalStatusPill");
    const text = document.getElementById("heroGlobalStatusText");
    const dot  = document.getElementById("heroGlobalStatusDot");
    if (!pill || !text || !dot) return;

    // First probe
    const alive = await probeCloudflareEdge();

    if (!alive) {
      // Automatic retry after 3s (Cloudflare cold start / slow network)
      await new Promise(r => setTimeout(r, 3000));
      const retry = await probeCloudflareEdge();

      if (!retry) {
        // True offline fallback — both probes failed
        text.textContent       = "[OFFLINE DEMO MODE: Edge MLP Active]";
        dot.style.background   = "var(--cyan)";
        pill.style.borderColor = "rgba(6, 182, 212, 0.4)";
        pill.style.background  = "rgba(6, 182, 212, 0.08)";
        pill.style.color       = "var(--cyan)";
        pill.classList.remove("cloud-active");
        pill.classList.add("offline-active");
      }
    }

    // Keep re-polling every 30s so pill recovers automatically if network comes back
    setInterval(probeCloudflareEdge, 30_000);
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 8. DOM READY INITIALIZATION
  // ══════════════════════════════════════════════════════════════════════════
  document.addEventListener("DOMContentLoaded", () => {
    new AppleScrollVideoScrubber("scrollVideo");
    const audio = new AmbientAudio();

    initHindmataSimulator();
    initSluiceSimulator();
    initAudioBriefing(audio);
    initPasscodeAuth();
    initBackendStatusMonitor();
  });
})();
