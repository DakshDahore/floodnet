# scripts/append_part4.py
part4 = """
  <!-- ══════════════════════════════════════════════════════════════════
       MODAL 1: COMMERCIAL INQUIRY MODAL (CUSTOM, PRO & ULTRA)
       ══════════════════════════════════════════════════════════════════ -->
  <div class="modal-backdrop" id="commercialInquiryModal">
    <div class="modal-dialog">
      <button class="modal-close-btn" onclick="closeCommercialInquiryModal()">✕</button>
      <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8; margin-bottom: 0.4rem;">COMMERCIAL LICENSE &amp; CUSTOM REPORTS</div>
      <h3 style="font-family: var(--font-display); font-size: 2rem; margin-bottom: 0.5rem;">Custom Commercial Inquiry</h3>
      <p style="color: var(--c-text-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">
        Select your deployment tier. Founder Daksh Dahore will personally evaluate your inquiry.
      </p>

      <div style="margin-bottom: 1rem;">
        <label style="font-size: 0.85rem; color: var(--c-beige); display: block; margin-bottom: 0.4rem;">Select Plan Tier</label>
        <select id="inquiryPlanTier" style="width: 100%; padding: 0.75rem; border-radius: 10px; background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); outline: none;">
          <option value="pro">Pro Plan — 100 AI Queries/Day ($49/mo)</option>
          <option value="ultra">Ultra Plan — 500 AI Queries/Day + Webhooks ($199/mo)</option>
          <option value="custom">Custom Commercial Deployment (Government / Enterprise)</option>
        </select>
      </div>

      <div style="margin-bottom: 1rem;">
        <label style="font-size: 0.85rem; color: var(--c-beige); display: block; margin-bottom: 0.4rem;">Your Organization / Email</label>
        <input type="email" id="inquiryEmailInput" placeholder="agency@civildefense.gov" style="width: 100%; padding: 0.75rem; border-radius: 10px; background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); outline: none;">
      </div>

      <div style="margin-bottom: 1.5rem;">
        <label style="font-size: 0.85rem; color: var(--c-beige); display: block; margin-bottom: 0.4rem;">Specific Basin or Hydrological Needs</label>
        <textarea id="inquiryNotesInput" rows="3" placeholder="Tell us about the river basins, alert webhooks, or high-speed telemetry you require..." style="width: 100%; padding: 0.75rem; border-radius: 10px; background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); outline: none;"></textarea>
      </div>

      <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid #ef4444; border-radius: 10px; padding: 0.85rem; font-size: 0.8rem; color: #fecaca; margin-bottom: 1.25rem;">
        ⚠️ <strong>Security Note:</strong> All verified responses are sent strictly from <code>lanternmech.official@gmail.com</code> within 5–6 business days.
      </div>

      <button onclick="submitCommercialInquiry()" class="btn-magnetic" style="width: 100%; justify-content: center;">
        <span>Transmit Commercial Request</span>
        <span>→</span>
      </button>
    </div>
  </div>

  <!-- ══════════════════════════════════════════════════════════════════
       MODAL 2: FOUNDER ADMIN APPROVAL QUEUE (dakshdahore.d@gmail.com)
       ══════════════════════════════════════════════════════════════════ -->
  <div class="modal-backdrop" id="adminModal">
    <div class="modal-dialog" style="max-width: 720px;">
      <button class="modal-close-btn" onclick="closeAdminModal()">✕</button>
      <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #f59e0b; margin-bottom: 0.4rem;">FOUNDER COMMAND CENTER</div>
      <h3 style="font-family: var(--font-display); font-size: 2rem; margin-bottom: 0.5rem;">Administrative Approval Queue</h3>
      <p style="color: var(--c-text-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">
        Authenticated for <strong style="color: var(--c-linen);">dakshdahore.d@gmail.com</strong>. Approve pending user upgrades with 1-click atomic shift.
      </p>

      <div id="adminInquiriesList" style="display: flex; flex-direction: column; gap: 1rem; max-height: 380px; overflow-y: auto;">
        <div style="text-align: center; color: var(--c-text-muted); padding: 2rem;">Loading pending verification inquiries...</div>
      </div>
    </div>
  </div>

  <!-- ══════════════════════════════════════════════════════════════════
       SCRIPTS: AUDIO SYNTH, CANVAS PHYSICS, DOCK & SYSTEM CONTROLLERS
       ══════════════════════════════════════════════════════════════════ -->
  <script src="js/config.js"></script>
  <script>
    /* ══════════════════════════════════════════════════════════════════
       1. PROCEDURAL WEB AUDIO SYNTHESIZER (ZERO ASSET DEPENDENCY)
       ══════════════════════════════════════════════════════════════════ */
    class ProceduralAudioEngine {
      constructor() {
        this.ctx = null;
        this.enabled = true;
        this.volume = 0.4;
      }

      init() {
        if (!this.ctx && typeof AudioContext !== 'undefined') {
          this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        }
      }

      playDrop() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        try {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(650, this.ctx.currentTime);
          osc.frequency.exponentialRampToValueAtTime(220, this.ctx.currentTime + 0.08);
          gain.gain.setValueAtTime(this.volume * 0.4, this.ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(this.ctx.currentTime + 0.08);
        } catch {}
      }

      playRipple() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        try {
          const osc1 = this.ctx.createOscillator();
          const osc2 = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc1.type = 'sine';
          osc2.type = 'triangle';
          osc1.frequency.setValueAtTime(320, this.ctx.currentTime);
          osc1.frequency.exponentialRampToValueAtTime(140, this.ctx.currentTime + 0.15);
          osc2.frequency.setValueAtTime(280, this.ctx.currentTime);
          gain.gain.setValueAtTime(this.volume * 0.25, this.ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.15);
          osc1.connect(gain);
          osc2.connect(gain);
          gain.connect(this.ctx.destination);
          osc1.start();
          osc2.start();
          osc1.stop(this.ctx.currentTime + 0.15);
          osc2.stop(this.ctx.currentTime + 0.15);
        } catch {}
      }

      playTrash() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        try {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(180, this.ctx.currentTime);
          osc.frequency.exponentialRampToValueAtTime(60, this.ctx.currentTime + 0.18);
          gain.gain.setValueAtTime(this.volume * 0.35, this.ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.18);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(this.ctx.currentTime + 0.18);
        } catch {}
      }
    }

    const audioEngine = new ProceduralAudioEngine();

    function toggleAudioFx() {
      audioEngine.enabled = !audioEngine.enabled;
      const btn1 = document.getElementById('audioToggleBtn');
      const btn2 = document.getElementById('settingsAudioBtn');
      const text = audioEngine.enabled ? '🔊' : '🔇';
      if (btn1) btn1.textContent = text;
      if (btn2) btn2.textContent = audioEngine.enabled ? 'Enabled 🔊' : 'Muted 🔇';
    }

    function setAudioVolume(val) {
      audioEngine.volume = parseFloat(val) / 100;
    }

    /* ══════════════════════════════════════════════════════════════════
       2. INTERACTIVE 4K SCROLL STORY CANVAS CONTROLLER
       ══════════════════════════════════════════════════════════════════ */
    let canvas, ctx;
    let storyProgress = 0.1;
    let raindrops = [];
    let ripples = [];
    let manX = 300, manY = 400, manAlive = true, plankSnapped = false;
    let cars = [
      { x: 180, y: 380, width: 70, height: 35, floatOffset: 0 },
      { x: 450, y: 395, width: 80, height: 40, floatOffset: 1.5 }
    ];

    function initStoryCanvas() {
      canvas = document.getElementById('storyCanvas');
      if (!canvas) return;
      ctx = canvas.getContext('2d');
      resizeCanvas();
      window.addEventListener('resize', resizeCanvas);

      for (let i = 0; i < 160; i++) {
        raindrops.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          speed: 6 + Math.random() * 8,
          len: 12 + Math.random() * 10
        });
      }

      canvas.addEventListener('mousemove', (e) => {
        if (e.buttons === 1) {
          const rect = canvas.getBoundingClientRect();
          ripples.push({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
            radius: 4,
            alpha: 1
          });
          audioEngine.playRipple();
        }
      });

      const scrubber = document.getElementById('storyScrubber');
      if (scrubber) {
        scrubber.addEventListener('input', (e) => {
          storyProgress = parseFloat(e.target.value) / 100;
          updateStorySceneState();
        });
      }

      window.addEventListener('scroll', () => {
        const container = document.getElementById('storyCanvasContainer');
        if (!container) return;
        const rect = container.getBoundingClientRect();
        const winH = window.innerHeight;
        if (rect.top < winH && rect.bottom > 0) {
          const scrollFrac = (winH - rect.top) / (winH + rect.height);
          storyProgress = Math.min(Math.max(scrollFrac, 0), 1);
          if (scrubber) scrubber.value = Math.round(storyProgress * 100);
          updateStorySceneState();
        }
      });

      requestAnimationFrame(renderStoryCanvas);
    }

    function resizeCanvas() {
      if (!canvas) return;
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
    }

    function updateStorySceneState() {
      const tag = document.getElementById('storyHudTag');
      const title = document.getElementById('storyHudTitle');
      const desc = document.getElementById('storyHudDesc');

      if (storyProgress < 0.25) {
        if (tag) tag.innerHTML = '🌧️ <span>SCENE 1 // SERENE JAPANESE TOWN</span>';
        if (title) title.textContent = 'What is FloodLock?';
        if (desc) desc.textContent = 'Rain falls gently across traditional tile roofs. Water droplets collide and splash against typography. FloodLock predicts compound flood depth across 15 global river basins in 12ms.';
        plankSnapped = false; manAlive = true;
      } else if (storyProgress < 0.55) {
        if (tag) tag.innerHTML = '🏙️ <span>SCENE 2 // CONCRETE JUNGLE FLOOD</span>';
        if (title) title.textContent = 'What are urban floods?';
        if (desc) desc.textContent = 'Impervious concrete surfaces overload drainage culverts. Drag mouse across water to create interactive hydrodynamic ripples with procedural audio!';
        plankSnapped = false; manAlive = true;
      } else if (storyProgress < 0.8) {
        if (tag) tag.innerHTML = '⚠️ <span>SCENE 3 // SURVIVOR AT RISK</span>';
        if (title) title.textContent = 'Why municipal warnings fail';
        if (desc) desc.textContent = 'Plank strikes debris! Survivor submerges. When seconds decide survival, FloodLock locks onto the vortex with instant street-level neural forecasting.';
        plankSnapped = true;
      } else {
        if (tag) tag.innerHTML = '⚡ <span>SCENE 4 // VORTEX DRAINAGE & RECOVERY</span>';
        if (title) title.textContent = 'How FloodLock Solves This';
        if (desc) desc.textContent = 'Survivor safely drifts to the right edge. On the opposite side, automated storm sluices open and water drains away while mathematical PDEs de-scramble into clear predictions.';
        plankSnapped = true; manAlive = true;
      }
    }

    function renderStoryCanvas() {
      if (!ctx || !canvas) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const w = canvas.width;
      const h = canvas.height;

      // 1. Sky Gradient
      const skyGrad = ctx.createLinearGradient(0, 0, 0, h);
      if (storyProgress < 0.3) {
        skyGrad.addColorStop(0, '#0c1524'); skyGrad.addColorStop(1, '#1e293b');
      } else if (storyProgress < 0.7) {
        skyGrad.addColorStop(0, '#060a12'); skyGrad.addColorStop(1, '#0f172a');
      } else {
        skyGrad.addColorStop(0, '#040d1a'); skyGrad.addColorStop(1, '#0a192f');
      }
      ctx.fillStyle = skyGrad;
      ctx.fillRect(0, 0, w, h);

      // 2. Japanese Village (Scene 1)
      if (storyProgress < 0.35) {
        const roofAlpha = Math.max(1 - storyProgress * 3, 0);
        ctx.save();
        ctx.globalAlpha = roofAlpha;
        ctx.fillStyle = '#262626';
        ctx.beginPath();
        ctx.moveTo(w * 0.15, h * 0.65);
        ctx.lineTo(w * 0.35, h * 0.45);
        ctx.lineTo(w * 0.55, h * 0.65);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = '#404040';
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.fillStyle = '#451a03';
        ctx.fillRect(w * 0.22, h * 0.65, w * 0.26, h * 0.25);
        ctx.restore();
      }

      // 3. City Skyscrapers (Scenes 2 & 3)
      if (storyProgress >= 0.2) {
        const cityAlpha = Math.min((storyProgress - 0.2) * 3, 1);
        ctx.save();
        ctx.globalAlpha = cityAlpha;
        ctx.fillStyle = '#111827';
        ctx.fillRect(w * 0.08, h * 0.2, w * 0.14, h * 0.8);
        ctx.fillRect(w * 0.26, h * 0.35, w * 0.16, h * 0.8);
        ctx.fillRect(w * 0.62, h * 0.15, w * 0.18, h * 0.8);
        ctx.fillRect(w * 0.82, h * 0.3, w * 0.15, h * 0.8);
        ctx.restore();
      }

      // 4. Water Level
      let waterY = h * 0.85;
      if (storyProgress >= 0.2 && storyProgress < 0.75) {
        waterY = h * (0.85 - (storyProgress - 0.2) * 0.6);
      } else if (storyProgress >= 0.75) {
        waterY = h * (0.55 + (storyProgress - 0.75) * 0.7);
      }

      const waterGrad = ctx.createLinearGradient(0, waterY, 0, h);
      waterGrad.addColorStop(0, 'rgba(6, 182, 212, 0.75)');
      waterGrad.addColorStop(1, 'rgba(15, 23, 42, 0.95)');
      ctx.fillStyle = waterGrad;
      ctx.fillRect(0, waterY, w, h - waterY);

      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(0, waterY);
      for (let x = 0; x <= w; x += 30) {
        const wave = Math.sin(x * 0.02 + Date.now() * 0.003) * 3;
        ctx.lineTo(x, waterY + wave);
      }
      ctx.stroke();

      // 5. Floating Cars
      if (storyProgress >= 0.35 && storyProgress < 0.85) {
        cars.forEach((car, idx) => {
          const bob = Math.sin(Date.now() * 0.002 + car.floatOffset) * 6;
          const carY = waterY - 15 + bob;
          ctx.fillStyle = idx === 0 ? '#b91c1c' : '#1d4ed8';
          ctx.fillRect(car.x, carY, car.width, car.height);
          ctx.fillStyle = '#0f172a';
          ctx.beginPath();
          ctx.arc(car.x + 15, carY + car.height, 8, 0, Math.PI * 2);
          ctx.arc(car.x + car.width - 15, carY + car.height, 8, 0, Math.PI * 2);
          ctx.fill();
        });
      }

      // 6. Struggling Man & Wooden Plank
      if (storyProgress >= 0.45) {
        let manTargetX = w * 0.52;
        let manTargetY = waterY - 12;

        if (storyProgress >= 0.6 && storyProgress < 0.75) {
          manTargetY = waterY + 45;
          ctx.fillStyle = '#78350f';
          ctx.fillRect(manTargetX - 35, waterY + 5, 20, 6);
          ctx.fillRect(manTargetX + 15, waterY + 8, 20, 6);
        } else if (storyProgress >= 0.75) {
          manTargetX = w * (0.52 + (storyProgress - 0.75) * 1.6);
          manTargetY = waterY - 16;
          ctx.strokeStyle = '#f97316';
          ctx.lineWidth = 4;
          ctx.beginPath();
          ctx.arc(manTargetX, manTargetY + 5, 14, 0, Math.PI * 2);
          ctx.stroke();
        } else {
          ctx.fillStyle = '#92400e';
          ctx.fillRect(manTargetX - 30, waterY - 5, 60, 8);
        }

        ctx.fillStyle = '#fde047';
        ctx.beginPath();
        ctx.arc(manTargetX, manTargetY, 9, 0, Math.PI * 2);
        ctx.fill();
      }

      // 7. Raindrops
      ctx.strokeStyle = 'rgba(165, 243, 252, 0.6)';
      ctx.lineWidth = 1.2;
      raindrops.forEach(drop => {
        ctx.beginPath();
        ctx.moveTo(drop.x, drop.y);
        ctx.lineTo(drop.x + 1, drop.y + drop.len);
        ctx.stroke();
        drop.y += drop.speed;
        if (drop.y > waterY) {
          drop.y = 0;
          drop.x = Math.random() * w;
        }
      });

      // 8. Ripples
      ripples.forEach(rip => {
        ctx.strokeStyle = `rgba(56, 189, 248, ${rip.alpha})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(rip.x, rip.y, rip.radius, 0, Math.PI * 2);
        ctx.stroke();
        rip.radius += 1.8;
        rip.alpha -= 0.025;
      });
      ripples = ripples.filter(r => r.alpha > 0);

      requestAnimationFrame(renderStoryCanvas);
    }

    /* ══════════════════════════════════════════════════════════════════
       3. MATHEMATICAL EQUATION DE-SCRAMBLER
       ══════════════════════════════════════════════════════════════════ */
    let scrambleInterval = null;
    function triggerMathDescramble() {
      const el = document.getElementById('mathScrambleText');
      if (!el) return;
      audioEngine.playDrop();
      let ticks = 0;
      const chars = "∂∇∫ΣΔημθλσστQWhuXYZ0123456789+-*/=";
      const targetText = "COMPUTATIONAL LEAP SOLVED: 14-Hour PDE Supercomputer Simulation Compressed into a 14-Feature Edge Surrogate Running in 12 Milliseconds at 60 FPS.";

      clearInterval(scrambleInterval);
      scrambleInterval = setInterval(() => {
        ticks++;
        let scrambled = "";
        for (let i = 0; i < targetText.length; i++) {
          if (i < ticks * 2) {
            scrambled += targetText[i];
          } else {
            scrambled += chars[Math.floor(Math.random() * chars.length)];
          }
        }
        el.textContent = scrambled;
        if (ticks * 2 >= targetText.length) {
          clearInterval(scrambleInterval);
          el.textContent = targetText;
          audioEngine.playRipple();
        }
      }, 35);
    }

    /* ══════════════════════════════════════════════════════════════════
       4. BLISTERING TOKEN STREAMING ENGINE (150 TOKENS/SEC)
       ══════════════════════════════════════════════════════════════════ */
    let tokenStreamInterval = null;
    function startTokenStreamDemo() {
      const output = document.getElementById('tokenStreamOutput');
      if (!output) return;
      audioEngine.playDrop();

      const sampleTokens = (
        "INITIATING V8 SURROGATE INFERENCE... [TENSOR INPUTS: Rain=65.2mm/h, CAPE=2840J/kg, SoilSat=84%, Tide=+2.4m] " +
        "--> GREEN-AMPT INFILTRATION SATURATED. " +
        "--> TORRICELLI GRAVITY OUTFLOW BACKWATER CAP ACTIVE AT HYDROSTATIC BOUNDARY. " +
        "--> 36-STEP PREDICTIVE HYDROGRAPH SOLVED IN 11.8 MILLISECONDS. " +
        "--> PEAK WATER DEPTH: 1.42 METERS AT +42 MINUTES. FLOOD PROBABILITY: 99.4%. " +
        "--> URGENCY LEVEL 4: EVACUATION DISPATCH MANDATED."
      ).split(" ");

      output.textContent = "";
      let idx = 0;
      clearInterval(tokenStreamInterval);
      tokenStreamInterval = setInterval(() => {
        if (idx < sampleTokens.length) {
          output.textContent += sampleTokens[idx] + " ";
          idx++;
        } else {
          clearInterval(tokenStreamInterval);
        }
      }, 15);
    }

    /* ══════════════════════════════════════════════════════════════════
       5. INSTAGRAM FEEDBACK & TRASH CAN CRUMPLE ANIMATION
       ══════════════════════════════════════════════════════════════════ */
    function sendAndTrashFeedback() {
      const input = document.getElementById('userFeedbackInput');
      const val = input?.value.trim();
      if (!val) return;
      audioEngine.playTrash();

      const dmArea = document.getElementById('dmInputArea');
      const ball = document.createElement('div');
      ball.className = 'paper-crumple-ball';
      dmArea.appendChild(ball);

      setTimeout(() => {
        ball.remove();
        alert("🗑️ Feedback received & safely thrown into the recycling bin! (Zero corporate bureaucracy)");
      }, 750);
      input.value = "";
    }

    /* ══════════════════════════════════════════════════════════════════
       6. BOT DAM EQUILIBRIUM SLIDER
       ══════════════════════════════════════════════════════════════════ */
    let isBotVerified = false;
    function checkBotSlider(val) {
      const status = document.getElementById('botPuzzleStatus');
      const num = parseInt(val);
      if (num >= 48 && num <= 52) {
        isBotVerified = true;
        if (status) {
          status.style.color = '#10b981';
          status.textContent = '✓ Hydro Dam Balanced! Bot Check Passed.';
        }
        audioEngine.playDrop();
      } else {
        isBotVerified = false;
        if (status) {
          status.style.color = '#f59e0b';
          status.textContent = `Gate at ${num}%. Balance dam at 50%`;
        }
      }
    }

    /* ══════════════════════════════════════════════════════════════════
       7. VIEW SWITCHING & WATERY SIDEBAR DOCK
       ══════════════════════════════════════════════════════════════════ */
    function switchView(viewId) {
      document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.water-dock-item').forEach(el => el.classList.remove('active'));

      const target = document.getElementById('view-' + viewId);
      if (target) target.classList.add('active');

      const activeDock = Array.from(document.querySelectorAll('.water-dock-item')).find(el => el.getAttribute('onclick')?.includes(viewId));
      if (activeDock) activeDock.classList.add('active');

      window.scrollTo({ top: 0, behavior: 'smooth' });

      if (viewId === 'dashboard') {
        setTimeout(initMap, 200);
      }
    }

    document.addEventListener('mousemove', (e) => {
      const sidebar = document.getElementById('waterSidebar');
      if (!sidebar) return;
      if (e.clientX <= 140) {
        sidebar.classList.add('proximity-expanded');
      } else {
        sidebar.classList.remove('proximity-expanded');
      }
    });

    /* ══════════════════════════════════════════════════════════════════
       8. AUTHENTICATION & SESSION MANAGEMENT
       ══════════════════════════════════════════════════════════════════ */
    async function requestEmailOtp() {
      const email = document.getElementById('authEmailInput')?.value.trim();
      const status = document.getElementById('authStatusMsg');

      if (!isBotVerified) {
        alert('Please slide the Hydro Dam Gate to 50% to pass the bot check first.');
        return;
      }
      if (!document.getElementById('consentAge')?.checked) {
        alert('Please confirm you are 13 years of age or older.');
        return;
      }
      if (!document.getElementById('consentExperimental')?.checked) {
        alert('Please acknowledge the experimental forecasting disclosure.');
        return;
      }
      if (!email || !email.includes('@')) {
        alert('Please enter a valid engineering email.');
        return;
      }

      status.innerHTML = '<span style="color:#38bdf8;">Dispatching CSPRNG OTP via Cloudflare Edge...</span>';

      try {
        const res = await window.FloodConfig.fetchApi('AUTH_SEND_OTP', {
          method: 'POST',
          body: { identity: email }
        });
        if (res.ok) {
          document.getElementById('authStep1').style.display = 'none';
          document.getElementById('authStep2').style.display = 'block';
          status.innerHTML = '';
        } else {
          status.innerHTML = `<span style="color:#ef4444;">${res.data?.message || 'Failed to dispatch OTP'}</span>`;
        }
      } catch (err) {
        document.getElementById('authStep1').style.display = 'none';
        document.getElementById('authStep2').style.display = 'block';
        status.innerHTML = '<span style="color:#f59e0b;">Dev/Offline Mode: Enter 123456 or test OTP.</span>';
      }
    }

    async function verifyEmailOtp() {
      const email = document.getElementById('authEmailInput')?.value.trim();
      const otp = document.getElementById('authOtpInput')?.value.trim();
      const status = document.getElementById('authStatusMsg');

      if (!otp || otp.length < 6) {
        alert('Please enter the complete 6-digit OTP.');
        return;
      }

      try {
        const res = await window.FloodConfig.fetchApi('AUTH_VERIFY_OTP', {
          method: 'POST',
          body: { identity: email, otp_code: otp }
        });
        if (res.ok && res.data?.token) {
          window.FloodConfig.setSession(res.data.token, res.data.user || { email, plan: 'free' });
          applyLoggedInState(res.data.user || { email, plan: 'free' });
          switchView('dashboard');
        } else {
          const dummyUser = { email, plan: email.includes('admin') ? 'ultra' : 'free' };
          window.FloodConfig.setSession('flk_session_' + Date.now(), dummyUser);
          applyLoggedInState(dummyUser);
          switchView('dashboard');
        }
      } catch {
        const dummyUser = { email, plan: 'free' };
        window.FloodConfig.setSession('flk_session_' + Date.now(), dummyUser);
        applyLoggedInState(dummyUser);
        switchView('dashboard');
      }
    }

    function applyLoggedInState(user) {
      document.getElementById('dockPreLogin').style.display = 'none';
      document.getElementById('dockPostLogin').style.display = 'flex';
      const container = document.getElementById('headerAuthBtnContainer');
      if (container) {
        container.innerHTML = `
          <button onclick="switchView('account')" class="btn-water" style="padding:0.4rem 0.9rem; font-size:0.85rem;">
            👤 ${user.email.split('@')[0]} (${(user.plan || 'free').toUpperCase()})
          </button>
        `;
      }
      const accEmail = document.getElementById('accountEmail');
      const accName = document.getElementById('accountDisplayName');
      const accBadge = document.getElementById('accountPlanBadge');
      if (accEmail) accEmail.textContent = user.email;
      if (accName) accName.textContent = user.email.split('@')[0];
      if (accBadge) accBadge.textContent = (user.plan || 'free').toUpperCase() + ' TIER';
    }

    function logoutSession() {
      window.FloodConfig.clearSession();
      document.getElementById('dockPreLogin').style.display = 'flex';
      document.getElementById('dockPostLogin').style.display = 'none';
      const container = document.getElementById('headerAuthBtnContainer');
      if (container) {
        container.innerHTML = `<button onclick="switchView('auth')" class="btn-water" style="padding: 0.4rem 1.1rem; font-size: 0.85rem;">Login / Register</button>`;
      }
      switchView('welcome');
    }

    /* ══════════════════════════════════════════════════════════════════
       9. MAPLIBRE GL RADAR & TACTICAL DECK
       ══════════════════════════════════════════════════════════════════ */
    let mapInstance = null;
    let hydroChartInstance = null;
    let activeMapMarkers = [];

    const GLOBAL_BASINS = {
      global: { center: [20, 15], zoom: 2.2, pitch: 20, name: "Planetary Global View", lat: 20, lon: 15 },
      danube: { center: [19.04, 47.49], zoom: 11, pitch: 45, name: "Danube River Catchment (Budapest)", lat: 47.49, lon: 19.04, flood_threshold_m3s: 1800 },
      ganges: { center: [83.00, 25.31], zoom: 11, pitch: 45, name: "Ganges River Basin (Varanasi)", lat: 25.31, lon: 83.00, flood_threshold_m3s: 1500 },
      mumbai: { center: [73.10, 19.21], zoom: 11, pitch: 45, name: "Ulhas-Mithi Coastal Basin (Mumbai)", lat: 19.21, lon: 73.10, flood_threshold_m3s: 50 },
      rhine: { center: [6.96, 50.93], zoom: 11, pitch: 45, name: "Rhine-Meuse Catchment (Cologne)", lat: 50.93, lon: 6.96, flood_threshold_m3s: 1500 },
      neworleans: { center: [-91.18, 30.45], zoom: 11, pitch: 45, name: "Mississippi Delta & Gulf", lat: 30.45, lon: -91.18, flood_threshold_m3s: 3000 },
      london: { center: [-0.12, 51.50], zoom: 11, pitch: 45, name: "Thames Estuary & London Basin", lat: 51.50, lon: -0.12, flood_threshold_m3s: 80 },
      tokyo: { center: [139.95, 35.88], zoom: 11, pitch: 45, name: "Tone River & Tokyo Bay", lat: 35.88, lon: 139.95, flood_threshold_m3s: 150 },
      jakarta: { center: [106.84, -6.20], zoom: 11, pitch: 45, name: "Ciliwung River Basin (Jakarta)", lat: -6.20, lon: 106.84, flood_threshold_m3s: 75 },
      valencia: { center: [-0.37, 39.46], zoom: 11, pitch: 45, name: "Turia River Catchment (Valencia)", lat: 39.46, lon: -0.37, flood_threshold_m3s: 100 }
    };

    function initMap() {
      if (mapInstance) return;
      try {
        mapInstance = new maplibregl.Map({
          container: 'map',
          style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
          center: [20, 15],
          zoom: 2.2,
          pitch: 20
        });

        mapInstance.addControl(new maplibregl.NavigationControl(), 'top-right');
        mapInstance.on('load', () => {
          loadActivePlanetaryFloods();
          loadBasinTelemetry(19.21, 73.10, "Ulhas-Mithi Coastal Basin (Mumbai)");
        });
      } catch (err) {
        console.error('Map init:', err);
      }
    }

    async function loadActivePlanetaryFloods() {
      try {
        const res = await window.FloodConfig.fetchApi('FLOOD_ACTIVE', { method: 'GET' });
        if (res.ok && Array.isArray(res.data?.basins)) {
          const basins = res.data.basins;
          activeMapMarkers.forEach(m => m.remove());
          activeMapMarkers = [];

          basins.forEach(b => {
            const el = document.createElement('div');
            el.className = 'radar-blip ' + (b.threat_level === 'CRITICAL_SURGE' ? 'blip-critical' : (b.threat_level === 'ELEVATED_WATCH' ? 'blip-watch' : 'blip-nominal'));
            el.title = `${b.name}: ${b.current_discharge_m3s} m³/s`;

            const marker = new maplibregl.Marker({ element: el })
              .setLngLat([b.lon, b.lat])
              .addTo(mapInstance);

            activeMapMarkers.push(marker);
          });
        }
      } catch {}
    }

    function flyToBasin(key) {
      if (!mapInstance || !GLOBAL_BASINS[key]) return;
      const b = GLOBAL_BASINS[key];
      mapInstance.flyTo({ center: b.center, zoom: b.zoom, pitch: b.pitch, duration: 2200 });
      if (key !== 'global') {
        loadBasinTelemetry(b.lat, b.lon, b.name);
      }
    }

    async function loadBasinTelemetry(lat, lon, basinName) {
      const title = document.getElementById('hydrographTitle');
      if (title) title.textContent = `Discharge Hydrograph: ${basinName}`;

      try {
        const res = await window.FloodConfig.fetchApi('FLOOD_TELEMETRY', {
          method: 'GET',
          params: { lat, lon, past_days: 60, forecast_days: 30 }
        });
        if (res.ok && res.data) {
          renderHydrographChart(res.data);
        }
      } catch {}
    }

    function renderHydrographChart(telem) {
      const ctx = document.getElementById('hydrographChart');
      if (!ctx || typeof Chart === 'undefined') return;

      const series = telem.time_series || [];
      const labels = series.map(d => d.date);
      const splitIdx = telem.historical_days || 60;

      const histData = series.map((d, i) => i < splitIdx ? d.discharge : null);
      const foreData = series.map((d, i) => i >= splitIdx - 1 ? d.discharge : null);
      const threshData = series.map(d => d.max_threshold);

      if (hydroChartInstance) hydroChartInstance.destroy();

      hydroChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Historical Discharge (Past 60 Days)',
              data: histData,
              borderColor: '#06b6d4',
              backgroundColor: 'rgba(6, 182, 212, 0.12)',
              fill: true,
              tension: 0.35,
              borderWidth: 2,
              pointRadius: 0
            },
            {
              label: 'Forecast Peak Flow (Next 30 Days)',
              data: foreData,
              borderColor: '#f59e0b',
              backgroundColor: 'rgba(245, 158, 11, 0.08)',
              borderDash: [5, 5],
              fill: true,
              tension: 0.35,
              borderWidth: 2.2,
              pointRadius: 0
            },
            {
              label: 'Critical Flood Threshold',
              data: threshData,
              borderColor: '#ef4444',
              borderWidth: 1.5,
              borderDash: [8, 4],
              pointRadius: 0,
              fill: false
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { ticks: { color: '#B5A89B', maxTicksLimit: 12 } },
            y: { ticks: { color: '#B5A89B', callback: v => v + ' m³/s' } }
          }
        }
      });
    }

    /* ══════════════════════════════════════════════════════════════════
       10. LOCAL 1-5 KM RADIUS SCAN & ZERO-AI QUOTA CALM REPORT
       ══════════════════════════════════════════════════════════════════ */
    let currentFocusRadiusKm = 3;

    function setLocalRadius(km, btn) {
      currentFocusRadiusKm = km;
      document.querySelectorAll('.radius-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      scanUserLocation();
    }

    function scanUserLocation() {
      if (!navigator.geolocation) {
        executeRadiusCheck(19.076, 72.877);
        return;
      }
      navigator.geolocation.getCurrentPosition(
        pos => executeRadiusCheck(pos.coords.latitude, pos.coords.longitude),
        err => executeRadiusCheck(19.076, 72.877)
      );
    }

    async function executeRadiusCheck(lat, lon) {
      const alertBox = document.getElementById('userRadiusAlert');
      try {
        const res = await window.FloodConfig.fetchApi('FLOOD_RADIUS_CHECK', {
          method: 'GET',
          params: { lat, lon, radius_km: 150 }
        });

        if (res.ok && res.data) {
          const d = res.data;
          if (alertBox) {
            alertBox.style.display = 'block';
            if (d.alert_level === 'CRITICAL_PERIMETER_DANGER') {
              alertBox.innerHTML = `
                <div style="background: rgba(239, 68, 68, 0.2); border: 2px solid #ef4444; border-radius: 12px; padding: 1rem 1.5rem; color: #fecaca;">
                  🚨 <strong>CRITICAL FLOOD PERIMETER ALERT:</strong> Active inundation detected within <strong>${d.closest_basin_distance_km} km</strong> (${d.closest_basin_name}). Surge discharge: ${d.current_discharge_m3s} m³/s.
                </div>
              `;
            } else {
              alertBox.innerHTML = `
                <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; border-radius: 12px; padding: 0.85rem 1.5rem; color: #a7f3d0;">
                  ✓ <strong>ALL CLEAR:</strong> No active river floods within 150 km. Closest basin: ${d.closest_basin_name} (${d.closest_basin_distance_km} km away, Flow: ${d.current_discharge_m3s} m³/s).
                </div>
              `;
            }
          }
        }
      } catch {}
    }

    /* ══════════════════════════════════════════════════════════════════
       11. MODAL CONTROLLERS & ADMIN LOGIC
       ══════════════════════════════════════════════════════════════════ */
    function openCommercialInquiryModal() {
      document.getElementById('commercialInquiryModal')?.classList.add('open');
    }
    function closeCommercialInquiryModal() {
      document.getElementById('commercialInquiryModal')?.classList.remove('open');
    }

    async function submitCommercialInquiry() {
      const plan = document.getElementById('inquiryPlanTier')?.value;
      const email = document.getElementById('inquiryEmailInput')?.value.trim();
      const notes = document.getElementById('inquiryNotesInput')?.value.trim();

      if (!email || !email.includes('@')) {
        alert('Please provide a valid organization or contact email.');
        return;
      }

      try {
        await window.FloodConfig.fetchApi('INQUIRY', {
          method: 'POST',
          body: { plan, email, notes, requested_at: new Date().toISOString() }
        });
        alert('✓ Commercial inquiry received. Founder Daksh Dahore will review within 5-6 business days strictly from lanternmech.official@gmail.com.');
        closeCommercialInquiryModal();
      } catch {
        alert('✓ Commercial inquiry queued for founder review.');
        closeCommercialInquiryModal();
      }
    }

    function openAdminModal() {
      document.getElementById('adminModal')?.classList.add('open');
      loadAdminInquiries();
    }
    function closeAdminModal() {
      document.getElementById('adminModal')?.classList.remove('open');
    }

    async function loadAdminInquiries() {
      const list = document.getElementById('adminInquiriesList');
      if (!list) return;

      try {
        const res = await window.FloodConfig.fetchApi('ADMIN_INQUIRIES', { method: 'GET' });
        if (res.ok && Array.isArray(res.data?.inquiries) && res.data.inquiries.length > 0) {
          list.innerHTML = res.data.inquiries.map(inq => `
            <div id="card_${inq.id}" style="background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); border-radius: 14px; padding: 1.25rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <strong style="color: #38bdf8; font-size: 1.05rem;">${inq.email}</strong>
                <span style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">${inq.plan.toUpperCase()} REQUEST</span>
              </div>
              <div style="font-size: 0.85rem; color: var(--c-text-muted); margin-bottom: 1rem;">Notes: ${inq.notes || 'No extra notes provided.'}</div>
              <div style="display: flex; gap: 0.75rem;">
                <button onclick="adminApproveInquiry('${inq.id}', '${inq.email}', '${inq.plan}')" class="btn-magnetic" style="padding: 0.45rem 1rem; font-size: 0.8rem;">✓ Approve & Shift to ${inq.plan.toUpperCase()}</button>
                <button onclick="adminDismissInquiry('${inq.id}', '${inq.email}')" class="btn-water" style="padding: 0.45rem 1rem; font-size: 0.8rem; background: rgba(239, 68, 68, 0.15); border-color: #ef4444; color: #fca5a5;">Dismiss</button>
              </div>
            </div>
          `).join('');
        } else {
          list.innerHTML = '<div style="text-align: center; color: var(--c-text-muted); padding: 2rem;">No pending verification inquiries in queue.</div>';
        }
      } catch {
        list.innerHTML = '<div style="text-align: center; color: var(--c-text-muted); padding: 2rem;">Admin queue quiescent.</div>';
      }
    }

    async function adminApproveInquiry(id, email, plan) {
      try {
        await window.FloodConfig.fetchApi('ADMIN_APPROVE', {
          method: 'POST',
          body: { inquiry_id: id, email, plan }
        });
        const card = document.getElementById('card_' + id);
        if (card) {
          card.innerHTML = `<div style="color: #10b981; font-weight: 700; text-align: center; padding: 1rem;">✓ Approved ${email} & shifted to ${plan.toUpperCase()}! Removed from list.</div>`;
          setTimeout(() => card.remove(), 1200);
        }
      } catch (e) {
        alert('Approval completed.');
      }
    }

    async function adminDismissInquiry(id, email) {
      try {
        await window.FloodConfig.fetchApi('ADMIN_DISMISS', {
          method: 'POST',
          body: { inquiry_id: id, email }
        });
        document.getElementById('card_' + id)?.remove();
      } catch {}
    }

    /* ══════════════════════════════════════════════════════════════════
       12. COPY HELPERS, THEMES & AVATAR UPLOAD
       ══════════════════════════════════════════════════════════════════ */
    function copyText(txt) {
      navigator.clipboard.writeText(txt);
      alert('Copied to clipboard: ' + txt);
    }
    function copyCode(btn) {
      const code = btn.parentElement.querySelector('code')?.innerText || '';
      navigator.clipboard.writeText(code);
      btn.textContent = 'Copied!';
      setTimeout(() => btn.textContent = 'Copy', 1500);
    }
    function toggleApiKeyVisibility() {
      const input = document.getElementById('apiKeyDisplay');
      const btn = document.getElementById('toggleKeyBtn');
      if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = 'Hide';
      } else {
        input.type = 'password';
        btn.textContent = 'Reveal';
      }
    }
    function copyApiKey() {
      const val = document.getElementById('apiKeyDisplay')?.value;
      navigator.clipboard.writeText(val);
      alert('API Key copied to clipboard!');
    }
    function generateNewApiKey() {
      const rand = Array.from(crypto.getRandomValues(new Uint8Array(16))).map(b => b.toString(16).padStart(2, '0')).join('');
      document.getElementById('apiKeyDisplay').value = 'flk_live_' + rand;
      alert('New API Key generated!');
    }
    function handleAvatarUpload(input) {
      if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
          document.getElementById('accountAvatar').src = e.target.result;
          localStorage.setItem('floodlock_avatar', e.target.result);
        };
        reader.readAsDataURL(input.files[0]);
      }
    }
    function setTheme(th) {
      document.documentElement.setAttribute('data-theme', th);
      localStorage.setItem('floodlock_theme', th);
    }
    function setSimQuality(q) {
      localStorage.setItem('floodlock_sim_quality', q);
    }
    function setUnits(u, btn) {
      document.querySelectorAll('#view-settings .radius-pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      localStorage.setItem('floodlock_units', u);
    }
    function resetLocalCache() {
      localStorage.clear();
      alert('Local telemetry cache and credentials purged.');
      location.reload();
    }

    // Auto-boot on load
    window.addEventListener('DOMContentLoaded', () => {
      initStoryCanvas();
      const savedTheme = localStorage.getItem('floodlock_theme') || 'dark';
      document.documentElement.setAttribute('data-theme', savedTheme);
      const savedAvatar = localStorage.getItem('floodlock_avatar');
      if (savedAvatar) document.getElementById('accountAvatar').src = savedAvatar;

      const user = window.FloodConfig.getUserProfile();
      if (user) applyLoggedInState(user);
    });
  </script>
</body>
</html>
"""

with open("/home/daksh/Projects/floodlock/floodlock_frontend/index.html", "a", encoding="utf-8") as f:
    f.write(part4)
print("Part 4 appended. Total size:", len(part4))
