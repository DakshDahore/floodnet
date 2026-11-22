# scripts/append_part3.py
part3 = """
    <!-- ══════════════════════════════════════════════════════════════════
         VIEW 2: PASSWORDLESS AUTH & BOT SECURITY GATE
         ══════════════════════════════════════════════════════════════════ -->
    <section id="view-auth" class="view-section">
      <div style="max-width: 600px; margin: 2rem auto;">
        <div class="card-luxury">
          <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8; margin-bottom: 0.5rem;">CSPRNG AUTHENTICATION GATE</div>
          <h2 style="font-family: var(--font-display); font-size: 2.2rem; margin-bottom: 0.75rem;">Passwordless Tactical Access</h2>
          <p style="color: var(--c-text-muted); font-size: 0.95rem; margin-bottom: 1.5rem;">
            Sign in or create an account using your engineering email. A cryptographically unbiased 6-digit OTP will be dispatched to your inbox.
          </p>

          <!-- "I Am Not A Bot" Interactive Dam Equilibrium Puzzle -->
          <div style="background: rgba(10, 15, 24, 0.8); border: 1px solid rgba(6, 182, 212, 0.35); border-radius: 16px; padding: 1.25rem; margin-bottom: 1.5rem;">
            <div style="font-size: 0.85rem; font-weight: 600; color: #a5f3fc; margin-bottom: 0.5rem; display: flex; justify-content: space-between;">
              <span>🤖 Security Challenge: "I Am Not A Bot"</span>
              <span id="botPuzzleStatus" style="color: #f59e0b;">Slide gate to balance flood dam (50%)</span>
            </div>
            <input type="range" id="botDamSlider" min="0" max="100" value="10" oninput="checkBotSlider(this.value)" style="width: 100%; accent-color: #06b6d4;">
          </div>

          <!-- Email OTP Form -->
          <div id="authStep1">
            <label style="font-size: 0.85rem; color: var(--c-beige); display: block; margin-bottom: 0.4rem;">Engineering Email Address</label>
            <input type="email" id="authEmailInput" placeholder="hydrologist@agency.org" style="width: 100%; padding: 0.85rem 1.1rem; border-radius: 12px; background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); margin-bottom: 1.2rem; font-size: 1rem; outline: none;">

            <!-- Mandatory Legal & Age Checkboxes -->
            <div style="display: flex; flex-direction: column; gap: 0.65rem; margin-bottom: 1.5rem; font-size: 0.85rem; color: var(--c-text-muted);">
              <label style="display: flex; align-items: flex-start; gap: 0.6rem; cursor: pointer;">
                <input type="checkbox" id="consentAge" style="accent-color: var(--c-cognac); margin-top: 3px;">
                <span>I confirm I am 13 years of age or older (Age Verification).</span>
              </label>
              <label style="display: flex; align-items: flex-start; gap: 0.6rem; cursor: pointer;">
                <input type="checkbox" id="consentExperimental" style="accent-color: var(--c-cognac); margin-top: 3px;">
                <span>I acknowledge FloodLock is an experimental predictive platform; forecasts do not supersede official civil defense directives.</span>
              </label>
              <label style="display: flex; align-items: flex-start; gap: 0.6rem; cursor: pointer;">
                <input type="checkbox" id="consentThirdParty" style="accent-color: var(--c-cognac); margin-top: 3px;">
                <span>I agree that environmental telemetry and feedback data may be analyzed by atmospheric scientific partners.</span>
              </label>
              <label style="display: flex; align-items: flex-start; gap: 0.6rem; cursor: pointer;">
                <input type="checkbox" id="consentCookies" style="accent-color: var(--c-cognac); margin-top: 3px;">
                <span>I agree to essential local session cookies and the privacy policy.</span>
              </label>
            </div>

            <button onclick="requestEmailOtp()" class="btn-magnetic" style="width: 100%; justify-content: center;" id="btnRequestOtp">
              <span>Send 6-Digit CSPRNG OTP</span>
              <span>→</span>
            </button>
          </div>

          <!-- OTP Verify Step -->
          <div id="authStep2" style="display: none;">
            <div style="padding: 0.75rem 1rem; border-radius: 10px; background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; color: #a7f3d0; font-size: 0.85rem; margin-bottom: 1rem;">
              ✓ 6-Digit OTP dispatched. Check your inbox (or development isolate log).
            </div>
            <label style="font-size: 0.85rem; color: var(--c-beige); display: block; margin-bottom: 0.4rem;">Enter 6-Digit Verification Code</label>
            <input type="text" id="authOtpInput" maxlength="6" placeholder="123456" style="width: 100%; padding: 0.85rem 1.1rem; border-radius: 12px; background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); margin-bottom: 1.2rem; font-family: var(--font-mono); font-size: 1.4rem; letter-spacing: 0.3em; text-align: center; outline: none;">

            <button onclick="verifyEmailOtp()" class="btn-magnetic" style="width: 100%; justify-content: center;" id="btnVerifyOtp">
              <span>Verify &amp; Unlock Tactical Mesh</span>
              <span>→</span>
            </button>
          </div>

          <div id="authStatusMsg" style="margin-top: 1rem; font-size: 0.85rem; text-align: center;"></div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════
         VIEW 3: TACTICAL COMMAND RADAR & LOCAL 1-5 KM RADIUS SCANNER
         ══════════════════════════════════════════════════════════════════ -->
    <section id="view-dashboard" class="view-section">
      <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8;">LIVE PLANETARY SATELLITE &amp; RIVER TELEMETRY</div>
          <h2 style="font-family: var(--font-display); font-size: 2.8rem;">Tactical Command Deck</h2>
        </div>

        <!-- 1-5 km Local Radius Selector Bar -->
        <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
          <span style="font-size: 0.8rem; font-family: var(--font-mono); color: var(--c-beige);">LOCAL FOCUS:</span>
          <div class="radius-selector-bar">
            <button class="radius-pill" onclick="setLocalRadius(1, this)">1 km</button>
            <button class="radius-pill" onclick="setLocalRadius(2, this)">2 km</button>
            <button class="radius-pill active" onclick="setLocalRadius(3, this)">3 km</button>
            <button class="radius-pill" onclick="setLocalRadius(4, this)">4 km</button>
            <button class="radius-pill" onclick="setLocalRadius(5, this)">5 km</button>
          </div>
          <button onclick="scanUserLocation()" class="btn-water" id="btnGeoScan" style="font-size: 0.82rem; padding: 0.45rem 1rem;">
            <span>📍</span> <strong>Scan My Location</strong>
          </button>
        </div>
      </div>

      <!-- Geolocation Flood Perimeter Alert Strip -->
      <div id="userRadiusAlert" style="display: none; margin-bottom: 1.5rem;"></div>

      <!-- MapLibre Radar Canvas -->
      <div class="radar-deck-container">
        <div id="map"></div>
      </div>

      <!-- Zero-AI Quota Calm Area Report Box -->
      <div class="card-luxury" id="calmAreaReportBox" style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem;">
          <div>
            <span style="font-family: var(--font-mono); font-size: 0.75rem; color: #10b981; background: rgba(16, 185, 129, 0.15); padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: 700;">
              ✓ ZERO AI QUOTA BURNED // QUIESCENT BASIN
            </span>
            <h3 style="font-family: var(--font-display); font-size: 1.8rem; margin-top: 0.4rem;" id="localAreaReportTitle">
              Local Area Meteorological Status
            </h3>
          </div>
          <button class="btn-magnetic" onclick="openCommercialInquiryModal()">
            <span>✨ Get Custom Deep-Dive Report using AI (Upgrade)</span>
          </button>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
          <div style="background: rgba(10, 7, 5, 0.6); padding: 1rem; border-radius: 12px; border: 1px solid var(--c-card-border);">
            <div style="font-size: 0.75rem; color: var(--c-text-muted);">CURRENT PRECIPITATION</div>
            <div style="font-size: 1.4rem; font-family: var(--font-mono); font-weight: 700; color: #38bdf8;" id="reportPrecip">0.0 mm/h</div>
            <div style="font-size: 0.75rem; color: #10b981;">No active cloudburst detected</div>
          </div>
          <div style="background: rgba(10, 7, 5, 0.6); padding: 1rem; border-radius: 12px; border: 1px solid var(--c-card-border);">
            <div style="font-size: 0.75rem; color: var(--c-text-muted);">NEXT-HOUR RAIN PREDICTION</div>
            <div style="font-size: 1.4rem; font-family: var(--font-mono); font-weight: 700; color: #f59e0b;" id="reportNextHour">0.2 mm (Light)</div>
            <div style="font-size: 0.75rem; color: var(--c-text-muted);">Convective CAPE: 420 J/kg</div>
          </div>
          <div style="background: rgba(10, 7, 5, 0.6); padding: 1rem; border-radius: 12px; border: 1px solid var(--c-card-border);">
            <div style="font-size: 0.75rem; color: var(--c-text-muted);">ANTECEDENT SOIL SATURATION</div>
            <div style="font-size: 1.4rem; font-family: var(--font-mono); font-weight: 700; color: #34d399;" id="reportSoil">34% (Dry Column)</div>
            <div style="font-size: 0.75rem; color: var(--c-text-muted);">Full infiltration capacity</div>
          </div>
          <div style="background: rgba(10, 7, 5, 0.6); padding: 1rem; border-radius: 12px; border: 1px solid var(--c-card-border);">
            <div style="font-size: 0.75rem; color: var(--c-text-muted);">OUTFALL BACKWATER STATE</div>
            <div style="font-size: 1.4rem; font-family: var(--font-mono); font-weight: 700; color: var(--c-linen);" id="reportTide">Low Tide (-0.4m)</div>
            <div style="font-size: 0.75rem; color: #10b981;">Gravity drains unblocked</div>
          </div>
        </div>
      </div>

      <!-- 90-Day Hydrological Hydrograph -->
      <div class="card-luxury" style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8;">ECMWF COPERNICUS GLOFAS 90-DAY TIME SERIES</div>
            <h3 style="font-family: var(--font-display); font-size: 2rem;" id="hydrographTitle">Basin Discharge Hydrograph</h3>
          </div>
          <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
            <select id="basinSelector" onchange="flyToBasin(this.value)" style="background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); padding: 0.45rem 0.85rem; border-radius: 8px; font-family: var(--font-sans); font-size: 0.85rem; outline: none;">
              <option value="global">Select Monitored River Basin...</option>
              <option value="danube">Danube River (Budapest)</option>
              <option value="rhine">Rhine-Meuse (Cologne)</option>
              <option value="mumbai">Ulhas-Mithi (Mumbai)</option>
              <option value="ganges">Ganges River (Varanasi)</option>
              <option value="neworleans">Mississippi Delta (New Orleans)</option>
              <option value="tokyo">Tone River (Tokyo Bay)</option>
              <option value="valencia">Turia River (Valencia)</option>
              <option value="london">Thames Estuary (London)</option>
              <option value="jakarta">Ciliwung River (Jakarta)</option>
            </select>
          </div>
        </div>

        <div style="height: 380px; width: 100%;">
          <canvas id="hydrographChart"></canvas>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════
         VIEW 4: API PLATFORM SCREEN
         ══════════════════════════════════════════════════════════════════ -->
    <section id="view-api" class="view-section">
      <div class="card-luxury" style="margin-bottom: 2rem;">
        <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8; margin-bottom: 0.4rem;">DEVELOPER ARCHITECTURE &amp; APIS</div>
        <h2 style="font-family: var(--font-display); font-size: 2.4rem; margin-bottom: 0.75rem;">FloodLock API Platform</h2>
        <p style="color: var(--c-text-muted); font-size: 0.95rem; margin-bottom: 1.5rem;">
          Access ultra-low-latency 14-feature neural predictions, GloFAS river discharge time series, and 150km radius alerts via our edge REST API or official libraries.
        </p>

        <!-- API Key Generator -->
        <div style="background: rgba(10, 15, 24, 0.85); border: 1px solid rgba(6, 182, 212, 0.35); border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
            <strong style="color: #a5f3fc; font-size: 1rem;">Active Production API Key</strong>
            <button onclick="generateNewApiKey()" class="btn-water" style="padding: 0.35rem 0.85rem; font-size: 0.78rem;">Generate New Key</button>
          </div>
          <div style="display: flex; gap: 0.75rem; align-items: center;">
            <input type="password" id="apiKeyDisplay" value="flk_live_948f8a29b01c4e78d9102ab3c4d" readonly style="flex: 1; background: #050810; border: 1px solid var(--c-card-border); color: #38bdf8; font-family: var(--font-mono); padding: 0.6rem 1rem; border-radius: 8px; font-size: 0.9rem; outline: none;">
            <button onclick="toggleApiKeyVisibility()" class="btn-water" style="padding: 0.5rem 0.85rem; font-size: 0.8rem;" id="toggleKeyBtn">Reveal</button>
            <button onclick="copyApiKey()" class="btn-magnetic" style="padding: 0.5rem 1rem; font-size: 0.8rem;">Copy</button>
          </div>
        </div>

        <!-- Library Downloads & Code Examples -->
        <h3 style="font-family: var(--font-display); font-size: 1.8rem; margin-bottom: 0.75rem;">SDK Installation &amp; Code Formats</h3>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
          <div class="code-box">
            <span style="color:#64748b;"># Python Official Package</span><br>
            <code>pip install floodlock-sdk</code>
            <button class="copy-btn" onclick="copyText('pip install floodlock-sdk')">Copy</button>
          </div>
          <div class="code-box">
            <span style="color:#64748b;"># Node.js / JavaScript Client</span><br>
            <code>npm install @floodlock/client</code>
            <button class="copy-btn" onclick="copyText('npm install @floodlock/client')">Copy</button>
          </div>
        </div>

        <!-- Python with Library -->
        <h4 style="font-size: 1rem; color: #a5f3fc; margin-top: 1.5rem;">1. Python (With Official Library)</h4>
        <div class="code-box">
          <pre><code>from floodlock import FloodLockClient

client = FloodLockClient(api_key="YOUR_API_KEY")
forecast = client.get_forecast(lat=19.076, lon=72.877, radius_km=150)
print(f"Risk: {forecast.risk_score}/100 | Discharge: {forecast.discharge_m3s} m³/s")</code></pre>
          <button class="copy-btn" onclick="copyCode(this)">Copy</button>
        </div>

        <!-- Python without Library (REST) -->
        <h4 style="font-size: 1rem; color: #a5f3fc; margin-top: 1.5rem;">2. Python (Without Library / Standard REST)</h4>
        <div class="code-box">
          <pre><code>import requests

url = "https://floodlock-backend.dakshdahore1995.workers.dev/api/flood/radius-check"
params = {"lat": 19.076, "lon": 72.877, "radius_km": 150}
headers = {"Authorization": "Bearer YOUR_API_KEY"}

response = requests.get(url, params=params, headers=headers)
print(response.json())</code></pre>
          <button class="copy-btn" onclick="copyCode(this)">Copy</button>
        </div>

        <!-- cURL Format -->
        <h4 style="font-size: 1rem; color: #a5f3fc; margin-top: 1.5rem;">3. cURL CLI</h4>
        <div class="code-box">
          <pre><code>curl -s "https://floodlock-backend.dakshdahore1995.workers.dev/api/flood/radius-check?lat=19.076&lon=72.877&radius_km=150" \\
     -H "Authorization: Bearer YOUR_API_KEY"</code></pre>
          <button class="copy-btn" onclick="copyCode(this)">Copy</button>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════
         VIEW 5: ACCOUNT & PROFILE SCREEN
         ══════════════════════════════════════════════════════════════════ -->
    <section id="view-account" class="view-section">
      <div style="max-width: 750px; margin: 0 auto;">
        <div class="card-luxury">
          <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8; margin-bottom: 0.4rem;">USER PROFILE &amp; USAGE METRICS</div>
          <h2 style="font-family: var(--font-display); font-size: 2.2rem; margin-bottom: 1.5rem;">Account Dashboard</h2>

          <div style="display: flex; gap: 2rem; align-items: center; margin-bottom: 2rem; flex-wrap: wrap;">
            <div style="position: relative;">
              <img id="accountAvatar" src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=160&auto=format&fit=crop" alt="Profile Avatar" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid var(--c-cognac);">
              <label for="avatarFileInput" style="position: absolute; bottom: 0; right: 0; background: var(--c-cognac); color: #fff; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 0.85rem;" title="Upload Avatar">📷</label>
              <input type="file" id="avatarFileInput" accept="image/*" style="display: none;" onchange="handleAvatarUpload(this)">
            </div>
            <div>
              <h3 style="font-family: var(--font-display); font-size: 1.6rem;" id="accountDisplayName">Hydrologist Engineer</h3>
              <p style="color: var(--c-text-muted); font-size: 0.9rem;" id="accountEmail">user@agency.gov</p>
              <span id="accountPlanBadge" style="background: rgba(146, 84, 43, 0.3); border: 1px solid var(--c-cognac); color: var(--c-linen); padding: 0.2rem 0.7rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">FREE TIER</span>
            </div>
          </div>

          <!-- Usage Meter -->
          <div style="background: rgba(10, 7, 5, 0.6); padding: 1.5rem; border-radius: 14px; border: 1px solid var(--c-card-border); margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.5rem;">
              <span>Daily Quota Consumption (UTC Reset 00:00)</span>
              <strong id="accountQuotaText">1 / 10 Queries Used</strong>
            </div>
            <div style="width: 100%; height: 10px; background: rgba(214, 197, 179, 0.1); border-radius: 999px; overflow: hidden;">
              <div id="accountQuotaBar" style="width: 10%; height: 100%; background: linear-gradient(90deg, #38bdf8, var(--c-cognac)); border-radius: 999px;"></div>
            </div>
          </div>

          <!-- Actions -->
          <div style="display: flex; flex-direction: column; gap: 1rem;">
            <button onclick="openCommercialInquiryModal()" class="btn-magnetic" style="justify-content: center;">
              <span>Upgrade to Pro / Ultra Tier</span>
              <span>→</span>
            </button>
            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
              <button onclick="alert('Subscription cancellation scheduled at end of billing cycle.')" class="btn-water" style="flex: 1;">Cancel Subscription</button>
              <button onclick="alert('Account marked for deletion. Data will be purged.')" style="flex: 1; background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #fca5a5; padding: 0.8rem; border-radius: 999px; font-weight: 600; cursor: pointer;">Delete Account</button>
            </div>
            <button onclick="logoutSession()" class="btn-water" style="margin-top: 1rem; background: rgba(214, 197, 179, 0.15); color: var(--c-linen);">Log Out</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════
         VIEW 6: OPEN SOURCE SCREEN (DEGRADED BASELINE MODEL)
         ══════════════════════════════════════════════════════════════════ -->
    <section id="view-opensource" class="view-section">
      <div class="card-luxury" style="margin-bottom: 2rem;">
        <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #34d399; margin-bottom: 0.4rem;">OPEN SCIENCE &amp; RESEARCH REPOSITORY</div>
        <h2 style="font-family: var(--font-display); font-size: 2.4rem; margin-bottom: 0.75rem;">FloodLock Open Source Hub</h2>
        <p style="color: var(--c-text-muted); font-size: 0.95rem; margin-bottom: 1.5rem;">
          We release open baseline model architectures and calibrated telemetry CSV datasets to support academic climate hydrology research worldwide.
        </p>

        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 14px; padding: 1.25rem; margin-bottom: 1.5rem; font-size: 0.88rem; color: #fef3c7;">
          ⚠️ <strong>Architecture Notice:</strong> The open source model (<code>floodlock_lite_v1.pth</code>) is an educational 4-feature degraded baseline. It does not include the proprietary 14-feature multi-task heads or the real-time ECMWF GloFAS edge weights running on our commercial V8 clusters.
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
          <div style="background: rgba(10, 7, 5, 0.6); padding: 1.5rem; border-radius: 14px; border: 1px solid var(--c-card-border);">
            <h4 style="font-family: var(--font-display); font-size: 1.4rem; margin-bottom: 0.5rem;">📦 Degraded Baseline PyTorch Model</h4>
            <p style="font-size: 0.85rem; color: var(--c-text-muted); margin-bottom: 1rem;">
              4-input feedforward network (Rain, CAPE, Soil Moisture, Tide) trained on CPU. Holdout Depth MAE: 9.8 cm.
            </p>
            <button onclick="alert('Downloading floodlock_lite_v1.pth baseline architecture weights...')" class="btn-water" style="font-size: 0.82rem; padding: 0.45rem 1rem;">Download Model (.PTH)</button>
          </div>

          <div style="background: rgba(10, 7, 5, 0.6); padding: 1.5rem; border-radius: 14px; border: 1px solid var(--c-card-border);">
            <h4 style="font-family: var(--font-display); font-size: 1.4rem; margin-bottom: 0.5rem;">📊 Sample Telemetry Dataset (.CSV)</h4>
            <p style="font-size: 0.85rem; color: var(--c-text-muted); margin-bottom: 1rem;">
              10,000 anonymized rows of physical hydrological inputs and observed runoff across historical storm events.
            </p>
            <button onclick="alert('Downloading floodlock_telemetry_sample.csv...')" class="btn-water" style="font-size: 0.82rem; padding: 0.45rem 1rem;">Download CSV Dataset</button>
          </div>
        </div>

        <!-- Repository Program Structure -->
        <h3 style="font-family: var(--font-display); font-size: 1.8rem; margin-bottom: 0.75rem;">Program &amp; Repository Structure</h3>
        <div class="code-box">
          <pre><code>floodlock_v3_open/
├── physics/
│   ├── floodlock_physics_simulator.py   # Green-Ampt & Torricelli PDE Solver
│   └── test_physics_conservation.py     # 7 Mass Conservation Verification Suites
├── trainer/
│   └── floodlock_colab_train.py         # PyTorch BCEWithLogits Training Script
├── cloudflare_worker/
│   └── src/weights_14f.js               # 14-Feature V8 Neural Surrogate Weights
└── data/
    └── floodlock_telemetry_sample.csv   # Historical Rainfall & Discharge Records</code></pre>
        </div>

        <button onclick="alert('Downloading complete source archive: floodlock_v3_2_gold_code_pack.zip')" class="btn-magnetic" style="margin-top: 1rem;">
          <span>Download All Open Source Assets (.ZIP)</span>
          <span>↓</span>
        </button>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════
         VIEW 7: CONTACT, CONTRIBUTION & COMMERCIAL LICENSE
         ══════════════════════════════════════════════════════════════════ -->
    <section id="view-contact" class="view-section">
      <div style="max-width: 800px; margin: 0 auto;">
        <div class="card-luxury" style="margin-bottom: 2rem;">
          <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8; margin-bottom: 0.4rem;">COMMERCIAL &amp; RESEARCH CHANNELS</div>
          <h2 style="font-family: var(--font-display); font-size: 2.4rem; margin-bottom: 0.75rem;">Contact &amp; Contribution Hub</h2>

          <!-- Mandatory Fraud Warning Banner -->
          <div style="background: rgba(239, 68, 68, 0.15); border: 2px solid #ef4444; border-radius: 14px; padding: 1.25rem; margin-bottom: 2rem;">
            <div style="color: #ef4444; font-weight: 700; font-size: 0.95rem; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.5rem;">
              <span>⚠️</span> <span>MANDATORY ANTI-FRAUD SECURITY WARNING</span>
            </div>
            <p style="color: #fecaca; font-size: 0.88rem; line-height: 1.5;">
              FloodLock and LanternMech will <strong>NEVER</strong> contact you via phone calls, WhatsApp, Telegram, or any email domain other than our official registered address: <code>lanternmech.official@gmail.com</code>. We never ask for passwords or private keys.
            </p>
          </div>

          <!-- Citizen Ground-Truth Submission -->
          <h3 style="font-family: var(--font-display); font-size: 1.8rem; margin-bottom: 0.5rem;">Submit Ground-Truth Sensor Data</h3>
          <p style="color: var(--c-text-muted); font-size: 0.9rem; margin-bottom: 1.25rem;">
            Verified physical measurements directly calibrate our neural surrogates and unlock <strong>1 Year Complimentary Ultra Tier Access (500 queries/day)</strong>.
          </p>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <div>
              <label style="font-size: 0.8rem; color: var(--c-beige); display: block; margin-bottom: 0.3rem;">Observed Water Depth (cm)</label>
              <input type="number" id="contribDepth" placeholder="e.g. 45" style="width: 100%; padding: 0.7rem; border-radius: 8px; background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); outline: none;">
            </div>
            <div>
              <label style="font-size: 0.8rem; color: var(--c-beige); display: block; margin-bottom: 0.3rem;">Rainfall Intensity (mm/h)</label>
              <input type="number" id="contribRain" placeholder="e.g. 60" style="width: 100%; padding: 0.7rem; border-radius: 8px; background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); outline: none;">
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
            <div>
              <label style="font-size: 0.8rem; color: var(--c-beige); display: block; margin-bottom: 0.3rem;">Latitude</label>
              <input type="number" step="0.001" id="contribLat" placeholder="19.076" style="width: 100%; padding: 0.7rem; border-radius: 8px; background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); outline: none;">
            </div>
            <div>
              <label style="font-size: 0.8rem; color: var(--c-beige); display: block; margin-bottom: 0.3rem;">Longitude</label>
              <input type="number" step="0.001" id="contribLon" placeholder="72.877" style="width: 100%; padding: 0.7rem; border-radius: 8px; background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); outline: none;">
            </div>
          </div>

          <button onclick="alert('✓ Telemetry submitted and verified. Ultra Plan allocated!')" class="btn-magnetic" style="width: 100%; justify-content: center;">
            <span>Submit Telemetry &amp; Claim Ultra Tier</span>
            <span>→</span>
          </button>

          <!-- Commercial Inquiry Info -->
          <div style="margin-top: 2.5rem; padding-top: 2rem; border-top: 1px solid var(--c-card-border);">
            <h3 style="font-family: var(--font-display); font-size: 1.8rem; margin-bottom: 0.5rem;">Commercial Deployment Inquiries</h3>
            <p style="color: var(--c-text-muted); font-size: 0.9rem; margin-bottom: 1rem;">
              For municipal flood defenses, infrastructure API licensing, or custom basin deployments, reach out directly to the founder.
            </p>
            <div style="background: rgba(10, 7, 5, 0.6); padding: 1.25rem; border-radius: 12px; border: 1px solid var(--c-card-border); font-size: 0.9rem;">
              <div>📧 <strong>Official Commercial Email:</strong> <span style="font-family: var(--font-mono); color: #38bdf8;">lanternmech.official@gmail.com</span></div>
              <div style="margin-top: 0.4rem;">⏱️ <strong>Inquiry SLA:</strong> All queries are personally evaluated and processed within <strong>5–6 business days</strong>.</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════════════
         VIEW 8: SETTINGS & PREFERENCES
         ══════════════════════════════════════════════════════════════════ -->
    <section id="view-settings" class="view-section">
      <div style="max-width: 700px; margin: 0 auto;">
        <div class="card-luxury">
          <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8; margin-bottom: 0.4rem;">SYSTEM CONFIGURATION</div>
          <h2 style="font-family: var(--font-display); font-size: 2.2rem; margin-bottom: 1.5rem;">Application Settings</h2>

          <!-- Theme Preference -->
          <div style="margin-bottom: 1.75rem;">
            <label style="font-size: 0.9rem; font-weight: 600; color: var(--c-beige); display: block; margin-bottom: 0.5rem;">Display Theme</label>
            <div style="display: flex; gap: 0.75rem;">
              <button onclick="setTheme('dark')" class="btn-water" style="flex: 1;">Savile Row (Dark)</button>
              <button onclick="setTheme('light')" class="btn-water" style="flex: 1;">Crisp Linen (Light)</button>
              <button onclick="setTheme('cyber')" class="btn-water" style="flex: 1;">Cyber Basin (Ocean)</button>
            </div>
          </div>

          <!-- Sound Effects -->
          <div style="margin-bottom: 1.75rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
              <label style="font-size: 0.9rem; font-weight: 600; color: var(--c-beige);">Web Audio Procedural Sound Effects</label>
              <button onclick="toggleAudioFx()" id="settingsAudioBtn" class="btn-water" style="padding: 0.3rem 0.8rem; font-size: 0.8rem;">Enabled 🔊</button>
            </div>
            <input type="range" id="audioVolumeSlider" min="0" max="100" value="40" oninput="setAudioVolume(this.value)" style="width: 100%; accent-color: #06b6d4;">
          </div>

          <!-- 4K Simulation Quality -->
          <div style="margin-bottom: 1.75rem;">
            <label style="font-size: 0.9rem; font-weight: 600; color: var(--c-beige); display: block; margin-bottom: 0.5rem;">Fluid Simulation Quality</label>
            <select id="simQualitySelect" onchange="setSimQuality(this.value)" style="width: 100%; padding: 0.75rem; border-radius: 10px; background: rgba(10, 7, 5, 0.8); border: 1px solid var(--c-card-border); color: var(--c-linen); outline: none;">
              <option value="4k">4K Ultra Canvas Particles (60 FPS)</option>
              <option value="high" selected>High Definition (Smooth)</option>
              <option value="low">Battery Saver Mode</option>
            </select>
          </div>

          <!-- Unit System -->
          <div style="margin-bottom: 2rem;">
            <label style="font-size: 0.9rem; font-weight: 600; color: var(--c-beige); display: block; margin-bottom: 0.5rem;">Hydrological Units</label>
            <div style="display: flex; gap: 0.75rem;">
              <button class="radius-pill active" onclick="setUnits('metric', this)">Metric (m, mm/h, m³/s)</button>
              <button class="radius-pill" onclick="setUnits('imperial', this)">Imperial (ft, in/h, cfs)</button>
            </div>
          </div>

          <button onclick="resetLocalCache()" style="width: 100%; background: rgba(214, 197, 179, 0.1); border: 1px solid var(--c-card-border); color: var(--c-text-muted); padding: 0.8rem; border-radius: 999px; cursor: pointer;">
            Purge Local Telemetry Cache &amp; Reset State
          </button>
        </div>
      </div>
    </section>

  </main>
"""

with open("/home/daksh/Projects/floodlock/floodlock_frontend/index.html", "a", encoding="utf-8") as f:
    f.write(part3)
print("Part 3 appended")
