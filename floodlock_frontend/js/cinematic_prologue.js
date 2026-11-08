/**
 * floodlock_frontend/js/cinematic_prologue.js
 * ────────────────────────────────────────────────────────────────────────────
 * 4K Cinematic Interactive Prologue & Audio Narrative Engine for FloodLock
 * 
 * Chapter Arc:
 *  0.00 - 0.25: The Monsoon Sky — Solitary crystalline raindrop falling from Mumbai storm clouds
 *  0.25 - 0.50: The Ground Impact — High-speed splash & radial ripples at Dadar TT Circle
 *  0.50 - 0.75: The Drain to Arabian Sea — Urban runoff meets the 3.87m spring tide (HYDRAULIC CHOKE)
 *  0.75 - 1.00: The Neural Sentinel — Submerged dive into 209-MLP mesh & Dadar TT Viaduct (+8.5m MSL)
 * 
 * Audio:
 *  - Generative Web Audio API ambient monsoon rain & deep thunder rumble (zero external files)
 *  - Web Speech API humanized narration with live animated equalizer & subtitle teleprompter
 */

(function () {
  "use strict";

  // ══════════════════════════════════════════════════════════════════════════
  // 1. STORY SCRIPT & EMOTIONAL CHRONOLOGY
  // ══════════════════════════════════════════════════════════════════════════
  const STORY_CHAPTERS = [
    {
      id: "skyfall",
      time: 0.0,
      title: "THE GENESIS // 26 JULY 2005",
      eyebrow: "MUMBAI MONSOON SKYFALL",
      quote: "One thousand and ninety-four lives were lost when the sky broke.",
      narration: "July twenty-sixth, two-thousand and five. Two o'clock in the afternoon. The skies above Mumbai ruptured, dumping nine hundred and forty-four millimeters of rain in twenty-four hours. Over one thousand and ninety-four citizens drowned in silent, rising waters. An entire metropolis was submerged.",
      statNumber: "1,094",
      statLabel: "LIVES EXTINGUISHED (2005)",
      accentColor: "#38bdf8"
    },
    {
      id: "impact",
      time: 0.28,
      title: "THE SAUCER BASIN // DADAR TT",
      eyebrow: "HINDMATA STREET IMPACT",
      quote: "A bowl carved into the city at 1.8 meters above sea level.",
      narration: "Every monsoon, raindrops strike the asphalt at Dadar TT and Dr. Ambedkar Road. Hindmata sits in a natural saucer basin, barely one point eight meters above sea level. In July twenty-twenty-three, trapped ambulances carrying critical patients drowned in road water. The storm drains had zero headroom.",
      statNumber: "+1.8m",
      statLabel: "BASIN ELEVATION (DADAR TT)",
      accentColor: "#f59e0b"
    },
    {
      id: "choke",
      time: 0.58,
      title: "THE ARABIAN TIDE // HYDRAULIC CHOKE",
      eyebrow: "MAHUL CREEK & LOVE GROVE OUTFALL",
      quote: "Gravity drainage cannot drain uphill into a four-meter sea.",
      narration: "The runoff rushes toward the Arabian Sea at Mahul Creek and Love Grove. But when high astronomical tide surges above three point zero meters, gravity drainage completely ceases. The ocean slams the sluice gates shut. Choked storm water forces itself backwards, vomiting out of city manholes.",
      statNumber: "100%",
      statLabel: "OUTFALL HYDRAULIC LOCK",
      accentColor: "#ef4444"
    },
    {
      id: "sentinel",
      time: 0.85,
      title: "THE NEURAL SENTINEL // ZERO LIVES LOST",
      eyebrow: "EDGE MLP & DADAR TT VIADUCT (+8.5m)",
      quote: "Engineered from tragedy. Predicting backflow before the curb floods.",
      narration: "Project FloodLock was born from this tragedy. Two-hundred and nine parameters, running in under fifty microseconds inside citizen browsers. When compound backflow is detected, Dadar TT Elevated Viaduct at eight point five meters opens immediately. Zero panic. Zero alarm fatigue. Zero lives lost.",
      statNumber: "0.05ms",
      statLabel: "IN-BROWSER EDGE LATENCY",
      accentColor: "#10b981"
    }
  ];

  // ══════════════════════════════════════════════════════════════════════════
  // 2. GENERATIVE WEB AUDIO API SYNTHESIZER (RAIN & THUNDER)
  // ══════════════════════════════════════════════════════════════════════════
  class AmbientStormAudio {
    constructor() {
      this.ctx = null;
      this.rainNode = null;
      this.rainGain = null;
      this.isPlaying = false;
      this.muted = false;
    }

    init() {
      if (this.ctx) return;
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      this.ctx = new AudioContext();

      // Create pink noise buffer for realistic rain sound
      const bufferSize = this.ctx.sampleRate * 2;
      const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const output = noiseBuffer.getChannelData(0);
      let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
      for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.96900 * b2 + white * 0.1538520;
        b3 = 0.86650 * b3 + white * 0.3104856;
        b4 = 0.55000 * b4 + white * 0.5329522;
        b5 = -0.7616 * b5 - white * 0.0168980;
        output[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.06;
        b6 = white * 0.115926;
      }

      this.noiseBuffer = noiseBuffer;
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.001, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);
    }

    startRain() {
      this.init();
      if (!this.ctx || this.isPlaying) return;
      if (this.ctx.state === "suspended") this.ctx.resume();

      const rainSource = this.ctx.createBufferSource();
      rainSource.buffer = this.noiseBuffer;
      rainSource.loop = true;

      // Bandpass filter for monsoon texture
      const filter = this.ctx.createBiquadFilter();
      filter.type = "lowpass";
      filter.frequency.setValueAtTime(1400, this.ctx.currentTime);

      this.rainGain = this.ctx.createGain();
      this.rainGain.gain.setValueAtTime(0.12, this.ctx.currentTime);

      rainSource.connect(filter);
      filter.connect(this.rainGain);
      this.rainGain.connect(this.masterGain);

      rainSource.start(0);
      this.rainSource = rainSource;

      // Fade in master gain
      this.masterGain.gain.exponentialRampToValueAtTime(this.muted ? 0.0001 : 0.22, this.ctx.currentTime + 1.5);
      this.isPlaying = true;
    }

    playThunder() {
      if (!this.ctx || !this.isPlaying || this.muted) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(75, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(28, this.ctx.currentTime + 2.4);

      gain.gain.setValueAtTime(0.35, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 2.5);

      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start();
      osc.stop(this.ctx.currentTime + 2.6);
    }

    toggleMute() {
      this.muted = !this.muted;
      if (this.masterGain && this.ctx) {
        this.masterGain.gain.setValueAtTime(this.muted ? 0.0001 : 0.22, this.ctx.currentTime);
      }
      return this.muted;
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 3. VOICE NARRATION & TELEPROMPTER ENGINE (WEB SPEECH API)
  // ══════════════════════════════════════════════════════════════════════════
  class StoryNarrator {
    constructor(onProgress) {
      this.onProgress = onProgress;
      this.synth = window.speechSynthesis;
      this.currentChapterIndex = -1;
      this.isSpeaking = false;
      this.isPaused = false;
      this.utterance = null;
      this.chosenVoice = null;
      this.initVoices();
    }

    initVoices() {
      if (!this.synth) return;
      const load = () => {
        const voices = this.synth.getVoices();
        // Prefer natural deep English voices
        this.chosenVoice = voices.find(v => v.lang.startsWith("en") && (v.name.includes("Natural") || v.name.includes("UK") || v.name.includes("Male") || v.name.includes("Google"))) ||
                           voices.find(v => v.lang.startsWith("en")) ||
                           voices[0];
      };
      load();
      if (this.synth.onvoiceschanged !== undefined) {
        this.synth.onvoiceschanged = load;
      }
    }

    playChapter(index) {
      if (index < 0 || index >= STORY_CHAPTERS.length) return;
      this.stop();

      const chapter = STORY_CHAPTERS[index];
      this.currentChapterIndex = index;
      this.isSpeaking = true;
      this.isPaused = false;

      if (this.onProgress) {
        this.onProgress(chapter, index, true);
      }

      if (!this.synth) return;

      const utter = new SpeechSynthesisUtterance(chapter.narration);
      utter.rate = 0.95; // deliberate, cinematic cadence
      utter.pitch = 0.92; // rich, somber gravitas
      if (this.chosenVoice) utter.voice = this.chosenVoice;

      utter.onend = () => {
        this.isSpeaking = false;
        if (this.onProgress) {
          this.onProgress(chapter, index, false);
        }
      };

      utter.onerror = (e) => {
        console.warn("[Narrator] Speech synthesis notice:", e);
        this.isSpeaking = false;
      };

      this.utterance = utter;
      this.synth.speak(utter);
    }

    playAllFromStart(onComplete) {
      let idx = 0;
      const step = () => {
        if (idx >= STORY_CHAPTERS.length) {
          if (onComplete) onComplete();
          return;
        }
        this.playChapter(idx);
        if (this.utterance) {
          this.utterance.onend = () => {
            idx++;
            setTimeout(step, 800);
          };
        } else {
          // Fallback timer if speech synth unavailable
          setTimeout(() => { idx++; step(); }, 7000);
        }
      };
      step();
    }

    togglePause() {
      if (!this.synth) return;
      if (this.synth.speaking) {
        if (this.synth.paused) {
          this.synth.resume();
          this.isPaused = false;
        } else {
          this.synth.pause();
          this.isPaused = true;
        }
      }
    }

    stop() {
      if (this.synth) this.synth.cancel();
      this.isSpeaking = false;
      this.isPaused = false;
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 4. 4K CINEMATIC CANVAS ANIMATOR (THE DROP TO SEA JOURNEY)
  // ══════════════════════════════════════════════════════════════════════════
  class CinematicCanvas {
    constructor(canvasId) {
      this.canvas = document.getElementById(canvasId);
      if (!this.canvas) return;
      this.ctx = this.canvas.getContext("2d");
      this.width = 0;
      this.height = 0;
      this.progress = 0; // 0.0 to 1.0 (scroll or chapter time)
      this.targetProgress = 0;
      this.particles = [];
      this.splashRipples = [];
      this.seaWaves = [];
      this.neuralNodes = [];
      this.lastThunderTime = 0;

      this.initDimensions();
      this.initObjects();
      window.addEventListener("resize", () => {
        this.initDimensions();
        this.initObjects();
      });

      this.loop = this.loop.bind(this);
      requestAnimationFrame(this.loop);
    }

    initDimensions() {
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      this.width = window.innerWidth;
      this.height = window.innerHeight;
      this.canvas.width = this.width * dpr;
      this.canvas.height = this.height * dpr;
      this.canvas.style.width = this.width + "px";
      this.canvas.style.height = this.height + "px";
      this.ctx.scale(dpr, dpr);
    }

    initObjects() {
      // 1. Rain streaks
      this.particles = [];
      const numRain = Math.min(160, Math.floor(this.width / 8));
      for (let i = 0; i < numRain; i++) {
        this.particles.push({
          x: Math.random() * this.width,
          y: Math.random() * this.height,
          len: 15 + Math.random() * 25,
          speed: 14 + Math.random() * 16,
          thickness: 1 + Math.random() * 1.5,
          opacity: 0.2 + Math.random() * 0.4
        });
      }

      // 2. Sea waves for Chapter 3
      this.seaWaves = [];
      for (let i = 0; i < 4; i++) {
        this.seaWaves.push({
          phase: i * 1.4,
          speed: 0.02 + i * 0.008,
          amplitude: 22 + i * 14,
          wavelength: 180 + i * 60,
          yBase: this.height * 0.65 + i * 25
        });
      }

      // 3. Neural nodes for Chapter 4
      this.neuralNodes = [];
      for (let i = 0; i < 24; i++) {
        this.neuralNodes.push({
          x: this.width * 0.15 + Math.random() * (this.width * 0.70),
          y: this.height * 0.30 + Math.random() * (this.height * 0.45),
          radius: 3 + Math.random() * 4,
          pulsePhase: Math.random() * Math.PI * 2,
          pulseSpeed: 0.04 + Math.random() * 0.03
        });
      }
    }

    triggerSplash(x, y) {
      for (let i = 0; i < 3; i++) {
        this.splashRipples.push({
          x: x || this.width * 0.5,
          y: y || this.height * 0.72,
          radius: 4 + i * 8,
          maxRadius: 180 + Math.random() * 80,
          opacity: 0.85,
          speed: 3 + Math.random() * 2.5
        });
      }
    }

    render(p) {
      const ctx = this.ctx;
      const w = this.width;
      const h = this.height;

      // Smooth progress interpolation
      this.progress += (this.targetProgress - this.progress) * 0.1;
      const prog = this.progress;

      // Deep atmospheric background fade based on chapter
      ctx.clearRect(0, 0, w, h);

      // Chapter-dependent sky ambient color
      let skyGradient;
      if (prog < 0.25) {
        // Storm clouds skyfall
        skyGradient = ctx.createLinearGradient(0, 0, 0, h);
        skyGradient.addColorStop(0, "#03060d");
        skyGradient.addColorStop(0.5, "#080f1e");
        skyGradient.addColorStop(1, "#0d1a33");
      } else if (prog < 0.55) {
        // Wet Asphalt Dadar TT
        skyGradient = ctx.createLinearGradient(0, 0, 0, h);
        skyGradient.addColorStop(0, "#080c14");
        skyGradient.addColorStop(0.65, "#0d1117");
        skyGradient.addColorStop(1, "#182030");
      } else if (prog < 0.80) {
        // Red Surge Choke at Arabian Sea
        skyGradient = ctx.createRadialGradient(w * 0.5, h * 0.7, 50, w * 0.5, h * 0.7, w);
        skyGradient.addColorStop(0, "#2a0914");
        skyGradient.addColorStop(0.6, "#13080e");
        skyGradient.addColorStop(1, "#07090e");
      } else {
        // Neural Viaduct Ascent
        skyGradient = ctx.createRadialGradient(w * 0.5, h * 0.5, 40, w * 0.5, h * 0.5, w);
        skyGradient.addColorStop(0, "#06222b");
        skyGradient.addColorStop(0.55, "#081119");
        skyGradient.addColorStop(1, "#07090e");
      }

      ctx.fillStyle = skyGradient;
      ctx.fillRect(0, 0, w, h);

      // ─── STAGE 1: RAINSTORMS & FALLING HERO DROP ───
      ctx.strokeStyle = "rgba(56, 189, 248, 0.35)";
      for (let i = 0; i < this.particles.length; i++) {
        const pt = this.particles[i];
        ctx.lineWidth = pt.thickness;
        ctx.beginPath();
        ctx.moveTo(pt.x, pt.y);
        ctx.lineTo(pt.x - 3.5, pt.y + pt.len);
        ctx.stroke();

        pt.y += pt.speed;
        pt.x -= 2.0;
        if (pt.y > h) {
          pt.y = -30;
          pt.x = Math.random() * w;
        }
      }

      // Hero Raindrop (Chapter 1 -> Chapter 2 falling animation)
      if (prog < 0.45) {
        const dropNorm = Math.min(1.0, prog / 0.30);
        const dropY = (h * 0.12) + dropNorm * (h * 0.60);
        const dropX = w * 0.50 + Math.sin(dropNorm * 6) * 12;

        // Glow halo
        const glow = ctx.createRadialGradient(dropX, dropY, 2, dropX, dropY, 24);
        glow.addColorStop(0, "rgba(56, 189, 248, 0.95)");
        glow.addColorStop(0.5, "rgba(6, 182, 212, 0.45)");
        glow.addColorStop(1, "rgba(6, 182, 212, 0.0)");
        ctx.fillStyle = glow;
        ctx.beginPath();
        ctx.arc(dropX, dropY, 24, 0, Math.PI * 2);
        ctx.fill();

        // Droplet tear shape
        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.arc(dropX, dropY, 5, 0, Math.PI);
        ctx.lineTo(dropX, dropY - 14);
        ctx.closePath();
        ctx.fill();

        // Trigger splash when drop lands
        if (dropNorm >= 0.95 && this.splashRipples.length === 0) {
          this.triggerSplash(dropX, dropY);
        }
      }

      // ─── STAGE 2: DADAR TT ROAD RIPPLES & ASPHALT REFLECTIONS ───
      if (prog >= 0.20 && prog < 0.70) {
        // Perspective road horizon line
        const roadY = h * 0.72;
        ctx.strokeStyle = "rgba(245, 158, 11, 0.18)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(0, roadY);
        ctx.lineTo(w, roadY);
        ctx.stroke();

        // Expanding splash ripples
        for (let i = this.splashRipples.length - 1; i >= 0; i--) {
          const rip = this.splashRipples[i];
          ctx.strokeStyle = `rgba(56, 189, 248, ${rip.opacity})`;
          ctx.lineWidth = 2.0;
          ctx.beginPath();
          ctx.ellipse(rip.x, rip.y, rip.radius, rip.radius * 0.35, 0, 0, Math.PI * 2);
          ctx.stroke();

          rip.radius += rip.speed;
          rip.opacity -= 0.009;
          if (rip.opacity <= 0) {
            this.splashRipples.splice(i, 1);
          }
        }

        // Ambient automatic splashes in heavy rain
        if (Math.random() < 0.08 && this.splashRipples.length < 8) {
          this.splashRipples.push({
            x: w * 0.20 + Math.random() * (w * 0.60),
            y: roadY + Math.random() * (h * 0.22),
            radius: 2,
            maxRadius: 60,
            opacity: 0.65,
            speed: 1.8 + Math.random() * 1.5
          });
        }
      }

      // ─── STAGE 3: ARABIAN SEA SURGE & OUTLET CHOKE ───
      if (prog >= 0.45 && prog < 0.88) {
        const chokeIntensity = Math.min(1.0, Math.max(0.0, (prog - 0.48) / 0.25));

        // Pulsing Crimson Tidal Warning Gate
        const gateX = w * 0.5;
        const gateY = h * 0.62;

        ctx.strokeStyle = `rgba(239, 68, 68, ${0.4 + chokeIntensity * 0.55})`;
        ctx.lineWidth = 3;
        ctx.strokeRect(gateX - 140, gateY - 60, 280, 120);

        ctx.fillStyle = `rgba(239, 68, 68, ${0.12 + chokeIntensity * 0.18})`;
        ctx.fillRect(gateX - 140, gateY - 60, 280, 120);

        // Choke Text overlay on canvas
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 13px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.fillText("LOVE GROVE SLUICE GATE (+3.0m)", gateX, gateY - 30);
        ctx.fillStyle = "#ef4444";
        ctx.font = "bold 18px 'JetBrains Mono', monospace";
        ctx.fillText(`HYDRAULIC CHOKE: ${Math.round(chokeIntensity * 100)}% LOCKED`, gateX, gateY + 5);
        ctx.font = "11px 'JetBrains Mono', monospace";
        ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
        ctx.fillText("ARABIAN SEA SPRING TIDE (+3.87m MSL) > DRAIN INVERT", gateX, gateY + 32);

        // Sinusoidal surging sea waves
        for (let i = 0; i < this.seaWaves.length; i++) {
          const wave = this.seaWaves[i];
          wave.phase += wave.speed;

          ctx.fillStyle = i === 0 ? "rgba(239, 68, 68, 0.15)" : `rgba(6, 182, 212, ${0.18 + i * 0.08})`;
          ctx.beginPath();
          ctx.moveTo(0, h);
          for (let x = 0; x <= w; x += 15) {
            const y = wave.yBase + Math.sin((x / wave.wavelength) + wave.phase) * wave.amplitude * (1 + chokeIntensity * 0.4);
            ctx.lineTo(x, y);
          }
          ctx.lineTo(w, h);
          ctx.closePath();
          ctx.fill();
        }
      }

      // ─── STAGE 4: NEURAL EDGE MLP & ELEVATED VIADUCT (+8.5m) ───
      if (prog >= 0.72) {
        const neuralNorm = Math.min(1.0, (prog - 0.72) / 0.25);

        // Viaduct Bridge Elevation Graphic
        const viaductY = h * 0.42;
        ctx.strokeStyle = "rgba(16, 185, 129, 0.85)";
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(w * 0.10, viaductY);
        ctx.lineTo(w * 0.90, viaductY);
        ctx.stroke();

        // Viaduct Pillars
        ctx.strokeStyle = "rgba(16, 185, 129, 0.35)";
        ctx.lineWidth = 2;
        for (let x = w * 0.20; x <= w * 0.80; x += w * 0.15) {
          ctx.beginPath();
          ctx.moveTo(x, viaductY);
          ctx.lineTo(x, viaductY + 140);
          ctx.stroke();
        }

        // Viaduct Status Badge
        ctx.fillStyle = "#10b981";
        ctx.font = "bold 15px 'JetBrains Mono', monospace";
        ctx.textAlign = "center";
        ctx.fillText("DADAR TT ELEVATED VIADUCT (+8.5m MSL) — 100% FLOOD RESILIENT", w * 0.5, viaductY - 20);
        ctx.fillStyle = "rgba(255, 255, 255, 0.75)";
        ctx.font = "12px 'JetBrains Mono', monospace";
        ctx.fillText("EMERGENCY VEHICLE & AMBULANCE DISPATCH PRIORITY CORRIDOR", w * 0.5, viaductY - 4);

        // Interconnected Neural Nodes
        ctx.strokeStyle = `rgba(6, 182, 212, ${0.25 * neuralNorm})`;
        ctx.lineWidth = 1;
        for (let i = 0; i < this.neuralNodes.length; i++) {
          for (let j = i + 1; j < this.neuralNodes.length; j++) {
            const dx = this.neuralNodes[i].x - this.neuralNodes[j].x;
            const dy = this.neuralNodes[i].y - this.neuralNodes[j].y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 180) {
              ctx.beginPath();
              ctx.moveTo(this.neuralNodes[i].x, this.neuralNodes[i].y);
              ctx.lineTo(this.neuralNodes[j].x, this.neuralNodes[j].y);
              ctx.stroke();
            }
          }
        }

        // Nodes Pulse
        for (let i = 0; i < this.neuralNodes.length; i++) {
          const node = this.neuralNodes[i];
          node.pulsePhase += node.pulseSpeed;
          const r = node.radius + Math.sin(node.pulsePhase) * 2;

          ctx.fillStyle = i % 2 === 0 ? "#06b6d4" : "#10b981";
          ctx.beginPath();
          ctx.arc(node.x, node.y, Math.max(1, r), 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }

    loop() {
      this.render();
      requestAnimationFrame(this.loop);
    }
  }

  // ══════════════════════════════════════════════════════════════════════════
  // 5. MASTER PROLOGUE CONTROLLER & DOM BINDINGS
  // ══════════════════════════════════════════════════════════════════════════
  document.addEventListener("DOMContentLoaded", () => {
    const audio = new AmbientStormAudio();
    const canvas = new CinematicCanvas("heroStormCanvas");

    // UI Elements
    const btnPlayVoice = document.getElementById("btnPlayStoryVoice");
    const btnMuteAudio = document.getElementById("btnMuteStormAudio");
    const teleprompterBox = document.getElementById("cinematicTeleprompter");
    const subtitleText = document.getElementById("prologueSubtitleText");
    const chapterBadge = document.getElementById("prologueChapterBadge");
    const quoteHeadline = document.getElementById("prologueQuoteHeadline");
    const statNumEl = document.getElementById("prologueStatNum");
    const statLabelEl = document.getElementById("prologueStatLabel");
    const scrubButtons = document.querySelectorAll(".story-scrub-btn");
    const waveBars = document.querySelectorAll(".audio-wave-bar");

    const updateUIForChapter = (chapter, index, isSpeaking) => {
      if (subtitleText) subtitleText.textContent = chapter.narration;
      if (chapterBadge) {
        chapterBadge.textContent = chapter.eyebrow;
        chapterBadge.style.borderColor = chapter.accentColor;
        chapterBadge.style.color = chapter.accentColor;
      }
      if (quoteHeadline) quoteHeadline.innerHTML = chapter.quote;
      if (statNumEl) {
        statNumEl.textContent = chapter.statNumber;
        statNumEl.style.color = chapter.accentColor;
      }
      if (statLabelEl) statLabelEl.textContent = chapter.statLabel;

      if (canvas) {
        canvas.targetProgress = chapter.time;
      }

      // Sync active button pill
      scrubButtons.forEach((btn, i) => {
        if (i === index) btn.classList.add("active");
        else btn.classList.remove("active");
      });

      // Wave animation toggle
      waveBars.forEach(b => {
        if (isSpeaking) b.classList.add("speaking");
        else b.classList.remove("speaking");
      });
    };

    const narrator = new StoryNarrator((chapter, index, isSpeaking) => {
      updateUIForChapter(chapter, index, isSpeaking);
      if (btnPlayVoice) {
        btnPlayVoice.innerHTML = isSpeaking ? "<span>⏸ PAUSE NARRATION</span>" : "<span>🎙️ PLAY CINEMATIC BRIEFING</span>";
      }
    });

    // 1. Play Narration Button
    if (btnPlayVoice) {
      btnPlayVoice.addEventListener("click", () => {
        audio.startRain();
        if (narrator.isSpeaking && !narrator.isPaused) {
          narrator.togglePause();
          btnPlayVoice.innerHTML = "<span>▶ RESUME NARRATION</span>";
          waveBars.forEach(b => b.classList.remove("speaking"));
        } else if (narrator.isPaused) {
          narrator.togglePause();
          btnPlayVoice.innerHTML = "<span>⏸ PAUSE NARRATION</span>";
          waveBars.forEach(b => b.classList.add("speaking"));
        } else {
          narrator.playAllFromStart(() => {
            btnPlayVoice.innerHTML = "<span>↺ REPLAY PROLOGUE</span>";
            waveBars.forEach(b => b.classList.remove("speaking"));
          });
        }
      });
    }

    // 2. Mute Audio Button
    if (btnMuteAudio) {
      btnMuteAudio.addEventListener("click", () => {
        const isMuted = audio.toggleMute();
        btnMuteAudio.textContent = isMuted ? "🔇 SOUND MUTED" : "🔊 AMBIENT RAIN ON";
        btnMuteAudio.classList.toggle("muted", isMuted);
      });
    }

    // 3. Scrub / Chapter Navigation Buttons
    scrubButtons.forEach((btn, idx) => {
      btn.addEventListener("click", () => {
        audio.startRain();
        narrator.playChapter(idx);
        if (idx === 2) audio.playThunder(); // Choke chapter thunder
      });
    });

    // 4. Scroll Sync Engine (Canvas adapts to scroll position)
    window.addEventListener("scroll", () => {
      const scrollY = window.scrollY;
      const heroHeight = window.innerHeight;
      const normScroll = Math.min(1.0, Math.max(0.0, scrollY / (heroHeight * 1.5)));

      // If narrator is idle, scroll controls canvas progress
      if (!narrator.isSpeaking && canvas) {
        canvas.targetProgress = normScroll;
      }
    }, { passive: true });

    // Initial state setup: Chapter 0
    updateUIForChapter(STORY_CHAPTERS[0], 0, false);
  });
})();
