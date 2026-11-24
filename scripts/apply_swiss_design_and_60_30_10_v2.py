import re

html_path = '/home/daksh/Documents/Projects/floodlock/floodlock_frontend/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════════════════════
# 1. GOOGLE FONTS: Ensure the exact 5 luxury pairings from Old Money & Mafia chart
# ═══════════════════════════════════════════════════════════════════════════
font_pattern = r'<link href="https://fonts\.googleapis\.com/css2\?family=[^"]+" rel="stylesheet">'
new_font_link = '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,400;1,600&family=Montserrat:wght@500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,400;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">'

if re.search(font_pattern, html):
    html = re.sub(font_pattern, new_font_link, html, count=1)
    print("1. Google Fonts link updated with Cinzel, Playfair Display, Cormorant Garamond, Plus Jakarta Sans, Montserrat.")

# ═══════════════════════════════════════════════════════════════════════════
# 2. COLOR ENGINE: :root (Dark 60-30-10) and [data-theme="light"] (Light 60-30-10)
# ═══════════════════════════════════════════════════════════════════════════
root_css = """:root {
      /* ══════════════════════════════════════════════════════════════════════
         DARK THEME: ONYX TRENCH & ANTIQUE GOLD (60 - 30 - 10 RULE)
         60% Canvas / Main: #121212 (Onyx Trench)
         30% Structural / Surfaces: #262626 (Slate Wool)
         10% High-Intent Accents & Focus: #B45309 (Antique Gold)
         ══════════════════════════════════════════════════════════════════════ */
      --c-bg: #121212;                           /* 60% Onyx Trench Canvas */
      --c-canvas: #121212;
      --c-surface: #1e1e1e;
      --c-card-bg: #262626;                      /* 30% Slate Wool Surfaces */
      --c-card-border: rgba(180, 83, 9, 0.28);   /* Antique Gold Fine Edge */
      --c-glass-shine: rgba(255, 255, 255, 0.08);

      /* Typography */
      --c-text-primary: #f5f5f5;                 /* Crisp Silk Ivory */
      --c-text-secondary: #d4d4d4;               /* Tailored Slate */
      --c-text-muted: #a3a3a3;                   /* Muted Wool */
      --c-linen: #f5f5f5;
      --c-beige: #d4d4d4;
      --c-obsidian: #121212;
      --c-umber: #1e1e1e;

      /* 10% Antique Gold Spectrum */
      --c-leather-light: #d97706;
      --c-leather: #B45309;                      /* 10% Antique Gold Accent */
      --c-leather-deep: #78350f;
      --c-cognac: #B45309;
      --c-cognac-hover: #d97706;
      --c-water: #B45309;
      --c-water-glow: rgba(180, 83, 9, 0.45);
      --c-accent: #B45309;
      --c-accent-hover: #d97706;
      --c-accent-glow: rgba(180, 83, 9, 0.35);

      /* Semantic Threat Colors */
      --c-ferrari: #dc2626;                      /* Urgent Red */
      --c-ferrari-glow: rgba(220, 38, 38, 0.35);
      --c-alert: #dc2626;
      --c-watch: #d97706;
      --c-nominal: #16a34a;

      /* Buttons & Action Controls (Montserrat uppercase) */
      --c-btn-primary-bg: #B45309;
      --c-btn-primary-text: #ffffff;
      --c-btn-primary-border: #d97706;
      --c-btn-secondary-bg: #262626;
      --c-btn-secondary-text: #f5f5f5;
      --c-btn-secondary-border: rgba(180, 83, 9, 0.38);

      /* Glass Proximity Sidebar */
      --c-dock-bg: rgba(26, 26, 26, 0.92);
      --c-dock-border: rgba(180, 83, 9, 0.32);
      --c-dock-shadow: rgba(0, 0, 0, 0.88);

      /* Typography Hierarchy */
      --font-hero: 'Cinzel', serif;
      --font-editorial: 'Playfair Display', Georgia, serif;
      --font-subheading: 'Cormorant Garamond', Georgia, serif;
      --font-body: 'Plus Jakarta Sans', -apple-system, sans-serif;
      --font-btn: 'Montserrat', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }"""

light_css = """[data-theme="light"] {
      /* ══════════════════════════════════════════════════════════════════════
         LIGHT THEME: CAMEL & ESPRESSO ROAST (60 - 30 - 10 RULE)
         60% Canvas / Main: #F5EFE6 (Camel Coat)
         30% Structural / Surfaces: #E6D8C3 (Sand Suede)
         10% High-Intent Accents & Focal: #451A03 (Espresso Roast)
         ══════════════════════════════════════════════════════════════════════ */
      --c-bg: #F5EFE6;                           /* 60% Camel Coat Canvas */
      --c-canvas: #F5EFE6;
      --c-surface: #EDE3D4;
      --c-card-bg: #E6D8C3;                      /* 30% Sand Suede Surfaces */
      --c-card-border: rgba(69, 26, 3, 0.22);    /* Espresso Roast Edge */
      --c-glass-shine: rgba(255, 255, 255, 0.7);

      /* Typography (Deep Espresso Roast — 100% Crisp Legibility) */
      --c-text-primary: #451A03;                 /* 10% Espresso Roast Key Headings */
      --c-text-secondary: #5c2b0a;
      --c-text-muted: #7a4e33;
      --c-linen: #451A03;
      --c-beige: #5c2b0a;
      --c-obsidian: #e2d3bd;
      --c-umber: #d4c2a8;

      /* 10% Espresso & Leather Spectrum */
      --c-leather-light: #5c2b0a;
      --c-leather: #451A03;                      /* Deep Espresso */
      --c-leather-deep: #2f1102;
      --c-cognac: #451A03;
      --c-cognac-hover: #2f1102;
      --c-water: #451A03;
      --c-water-glow: rgba(69, 26, 3, 0.35);
      --c-accent: #451A03;
      --c-accent-hover: #2f1102;
      --c-accent-glow: rgba(69, 26, 3, 0.25);

      /* Semantic Threat Colors */
      --c-ferrari: #b91c1c;
      --c-ferrari-glow: rgba(185, 28, 28, 0.25);
      --c-alert: #b91c1c;
      --c-watch: #b45309;
      --c-nominal: #15803d;

      /* Buttons & Action Controls (Montserrat uppercase) */
      --c-btn-primary-bg: #451A03;
      --c-btn-primary-text: #F5EFE6;
      --c-btn-primary-border: #2f1102;
      --c-btn-secondary-bg: #E6D8C3;
      --c-btn-secondary-text: #451A03;
      --c-btn-secondary-border: rgba(69, 26, 3, 0.38);

      /* Glass Proximity Sidebar */
      --c-dock-bg: rgba(230, 216, 195, 0.95);
      --c-dock-border: rgba(69, 26, 3, 0.25);
      --c-dock-shadow: rgba(69, 26, 3, 0.18);
    }"""

root_pattern = r':root\s*\{.*?\n    \}'
light_pattern = r'\[data-theme="light"\]\s*\{.*?\n    \}'

html = re.sub(root_pattern, root_css, html, flags=re.DOTALL)
html = re.sub(light_pattern, light_css, html, flags=re.DOTALL)
print("2. Updated :root and [data-theme='light'] color engines.")

# ═══════════════════════════════════════════════════════════════════════════
# 3. GLOBAL SWISS TYPOGRAPHY & SMOOTH ANIMATION RULES (NO BLUR LAG)
# ═══════════════════════════════════════════════════════════════════════════
# Replace line 870-884 scroll reveal with hardware-accelerated 120fps CSS:
old_scroll_reveal = r'\.scroll-reveal\s*\{[^}]*filter:\s*blur[^}]*\}\s*\.scroll-reveal\.revealed\s*\{[^}]*\}'
new_scroll_reveal = """.scroll-reveal {
      opacity: 0;
      transform: translateY(22px);
      transition: opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1),
                  transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
      will-change: opacity, transform;
      backface-visibility: hidden;
    }
    .scroll-reveal.revealed {
      opacity: 1;
      transform: translateY(0);
    }"""

html = re.sub(old_scroll_reveal, new_scroll_reveal, html, flags=re.DOTALL)

# Also fix the duplicate hero title giant styles and enforce Cinzel / Playfair Display / Montserrat
old_hero_title = r'\.hero-title-giant\s*\{[^}]+font-family:[^}]+(?=\.hero-title-giant\s*span|\.hero-subtitle-lead)'
new_hero_title = """.hero-title-giant {
      font-family: var(--font-hero) !important;
      font-size: clamp(2.8rem, 6.2vw, 5.2rem);
      font-weight: 800;
      line-height: 1.08;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      margin-bottom: 1.25rem;
      color: var(--c-text-primary);
    }"""

# Replace all instances of .hero-title-giant definitions
html = re.sub(r'\.hero-title-giant\s*\{[^}]*font-family:[^}]*\}', new_hero_title, html)

# Enforce Swiss Typography Hierarchy everywhere:
swiss_rules = """
    /* ══════════════════════════════════════════════════════════════════
       SWISS TYPOGRAPHY ENFORCEMENT & 60-30-10 HARMONY
       ══════════════════════════════════════════════════════════════════ */
    .brand-logo-text, .brand-title, .header-brand {
      font-family: var(--font-hero) !important;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    h1, h2, h3, h4, .chapter-heading-giant, .tri-pillar-title, .pipeline-step-title, .bento-title, .hero-stat-item h3 {
      font-family: var(--font-editorial) !important;
      letter-spacing: -0.01em;
    }

    .hero-subtitle-lead, .chapter-lead-text, .pull-quote {
      font-family: var(--font-subheading) !important;
      font-size: 1.22rem;
      line-height: 1.6;
    }

    body, p, span, div, input, textarea, select {
      font-family: var(--font-body);
    }

    button, .btn-keynote-primary, .btn-keynote-secondary, .btn-water, .btn-magnetic,
    .tri-pillar-badge, .pipeline-step-badge, .hero-badge-pill, .chapter-eyebrow, .dock-label,
    .hero-stat-lbl, .code-tab-btn, .tensor-chip-index {
      font-family: var(--font-btn) !important;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      font-weight: 700;
    }

    code, pre, .mono, [id*="quota"], [id*="status"], .hero-stat-num {
      font-family: var(--font-mono) !important;
    }

    .hero-title-giant span.gradient-cyan,
    .hero-title-giant span.gradient-accent {
      background: linear-gradient(135deg, #d97706 0%, #B45309 50%, #78350f 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    [data-theme="light"] .hero-title-giant span.gradient-cyan,
    [data-theme="light"] .hero-title-giant span.gradient-accent {
      background: linear-gradient(135deg, #5c2b0a 0%, #451A03 50%, #2f1102 100%) !important;
      -webkit-background-clip: text !important;
      -webkit-text-fill-color: transparent !important;
    }
"""

if '/* SWISS TYPOGRAPHY ENFORCEMENT' not in html:
    html = html.replace('/* ── Accessible Focus Ring ── */', swiss_rules + '\n    /* ── Accessible Focus Ring ── */')
    print("3. Injected Swiss Typography and font rules.")

# ═══════════════════════════════════════════════════════════════════════════
# 4. LIGHT MODE STYLING COMPREHENSIVE OVERRIDES (60% #F5EFE6, 30% #E6D8C3, 10% #451A03)
# ═══════════════════════════════════════════════════════════════════════════
light_mode_full_css = """
    /* ══════════════════════════════════════════════════════════════════
       60-30-10 LIGHT MODE COMPLETE HARMONY (CAMEL & ESPRESSO ROAST)
       ══════════════════════════════════════════════════════════════════ */
    [data-theme="light"] body {
      background-color: #F5EFE6 !important;
      color: #451A03 !important;
    }

    [data-theme="light"] .site-header {
      background: rgba(245, 239, 230, 0.92) !important;
      border-bottom: 1px solid rgba(69, 26, 3, 0.18) !important;
    }

    [data-theme="light"] .card-luxury,
    [data-theme="light"] .tri-pillar-card,
    [data-theme="light"] .pipeline-step-card,
    [data-theme="light"] .sovereign-banner,
    [data-theme="light"] .groq-testbench-card,
    [data-theme="light"] .bento-card,
    [data-theme="light"] .hero-stat-strip,
    [data-theme="light"] .split-slider-box {
      background: #E6D8C3 !important;
      border: 1px solid rgba(69, 26, 3, 0.22) !important;
      box-shadow: 0 10px 30px rgba(69, 26, 3, 0.08) !important;
      color: #451A03 !important;
    }

    [data-theme="light"] .chapter-heading-giant,
    [data-theme="light"] .tri-pillar-title,
    [data-theme="light"] .pipeline-step-title,
    [data-theme="light"] .bento-title,
    [data-theme="light"] h1, [data-theme="light"] h2, [data-theme="light"] h3, [data-theme="light"] h4 {
      color: #451A03 !important;
    }

    [data-theme="light"] .hero-title-giant {
      color: #451A03 !important;
      background: none !important;
      -webkit-text-fill-color: #451A03 !important;
    }

    [data-theme="light"] .hero-subtitle-lead,
    [data-theme="light"] .chapter-lead-text,
    [data-theme="light"] .tri-pillar-desc,
    [data-theme="light"] .pipeline-step-desc,
    [data-theme="light"] .bento-desc,
    [data-theme="light"] p {
      color: #5c2b0a !important;
    }

    [data-theme="light"] .chapter-eyebrow,
    [data-theme="light"] .tri-pillar-badge,
    [data-theme="light"] .pipeline-step-badge,
    [data-theme="light"] .hero-stat-lbl,
    [data-theme="light"] .bento-tag {
      color: #451A03 !important;
      background: rgba(69, 26, 3, 0.1) !important;
      border: 1px solid rgba(69, 26, 3, 0.25) !important;
    }

    [data-theme="light"] .hero-stat-num {
      color: #451A03 !important;
    }

    [data-theme="light"] .btn-keynote-primary,
    [data-theme="light"] .btn-water {
      background: #451A03 !important;
      color: #F5EFE6 !important;
      border: 1px solid #2f1102 !important;
      box-shadow: 0 8px 24px rgba(69, 26, 3, 0.22) !important;
    }

    [data-theme="light"] .btn-keynote-primary:hover,
    [data-theme="light"] .btn-water:hover {
      background: #2f1102 !important;
      color: #ffffff !important;
    }

    [data-theme="light"] .btn-keynote-secondary {
      background: #E6D8C3 !important;
      color: #451A03 !important;
      border: 1px solid rgba(69, 26, 3, 0.35) !important;
      box-shadow: 0 4px 14px rgba(69, 26, 3, 0.06) !important;
    }

    [data-theme="light"] .btn-keynote-secondary:hover {
      background: #dac7ad !important;
      color: #2f1102 !important;
    }

    [data-theme="light"] .tensor-chip {
      background: #E6D8C3 !important;
      border: 1px solid rgba(69, 26, 3, 0.25) !important;
      color: #451A03 !important;
    }

    [data-theme="light"] .tensor-chip.active {
      background: rgba(69, 26, 3, 0.16) !important;
      border-color: #451A03 !important;
    }

    [data-theme="light"] .tensor-chip-name {
      color: #451A03 !important;
    }

    [data-theme="light"] .tensor-chip-index {
      color: #78350f !important;
    }

    [data-theme="light"] .tensor-chip-physics {
      color: #5c2b0a !important;
    }

    [data-theme="light"] .code-terminal-deck {
      background: #2b170c !important;
      border: 1px solid rgba(69, 26, 3, 0.35) !important;
    }

    [data-theme="light"] input, [data-theme="light"] textarea, [data-theme="light"] select {
      background: #ffffff !important;
      border: 1px solid rgba(69, 26, 3, 0.32) !important;
      color: #451A03 !important;
    }

    [data-theme="light"] .water-sidebar {
      background: rgba(230, 216, 195, 0.94) !important;
      border: 1px solid rgba(69, 26, 3, 0.25) !important;
      box-shadow: 0 20px 50px rgba(69, 26, 3, 0.18) !important;
    }

    [data-theme="light"] .water-dock-item {
      color: #451A03 !important;
    }

    [data-theme="light"] .water-dock-item:hover {
      background: rgba(69, 26, 3, 0.14) !important;
      color: #2f1102 !important;
    }

    [data-theme="light"] .water-dock-item.active {
      background: rgba(69, 26, 3, 0.22) !important;
      border-color: #451A03 !important;
      color: #451A03 !important;
    }

    [data-theme="light"] .search-trigger-btn {
      background: #E6D8C3 !important;
      border: 1px solid rgba(69, 26, 3, 0.25) !important;
      color: #451A03 !important;
    }
"""

# Replace the previous light mode overrides
light_override_pattern = r'/\* ══════════════════════════════════════════════════════════════════\s*FLAWLESS LIGHT MODE COMPREHENSIVE FIXES.*?\}\s*(?=</style>)'
if re.search(light_override_pattern, html, flags=re.DOTALL):
    html = re.sub(light_override_pattern, light_mode_full_css.strip(), html, flags=re.DOTALL)
    print("4. Replaced light mode overrides with strict 60-30-10 palette.")

# ═══════════════════════════════════════════════════════════════════════════
# 5. DUAL GITHUB OAUTH CLIENT ROUTING: NETLIFY VS PAGES.DEV
# ═══════════════════════════════════════════════════════════════════════════
old_gh_login_pattern = r'function loginWithGitHub\(\)\s*\{.*?\n    \}'
new_gh_login = """function loginWithGitHub() {
      const cleanOrigin = window.location.origin.replace(/\\/+$/, '');
      const isPages = window.location.hostname.includes("pages.dev");

      // ── Dual GitHub Login Architecture ──
      if (isPages) {
        // Option A: Dedicated Pages.dev OAuth App Client ID
        const pagesClientId = window.FLOODLOCK_GH_CLIENT_ID_PAGES || "";
        if (pagesClientId) {
          const redirectUri = `${cleanOrigin}/auth/callback`;
          const stateObj = { origin: cleanOrigin, provider: "github", ts: Date.now() };
          const stateStr = encodeURIComponent(JSON.stringify(stateObj));
          window.location.href = `https://github.com/login/oauth/authorize?client_id=${encodeURIComponent(pagesClientId)}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=read:user%20user:email&state=${stateStr}`;
          return;
        }

        // Option B: Netlify OAuth Forwarding Bridge (Zero redirect_uri mismatch!)
        // Uses authorized client Ov23liHMgDQduw9y5SOT with callback https://metoflood.netlify.app/auth/callback.
        // Netlify callback detects origin=pages.dev and forwards code seamlessly.
        const netlifyClientId = "Ov23liHMgDQduw9y5SOT";
        const netlifyCallback = "https://metoflood.netlify.app/auth/callback";
        const stateObj = { origin: cleanOrigin, provider: "github", ts: Date.now() };
        const stateStr = encodeURIComponent(JSON.stringify(stateObj));
        window.location.href = `https://github.com/login/oauth/authorize?client_id=${encodeURIComponent(netlifyClientId)}&redirect_uri=${encodeURIComponent(netlifyCallback)}&scope=read:user%20user:email&state=${stateStr}`;
      } else {
        // Standard Netlify Direct OAuth
        const netlifyClientId = "Ov23liHMgDQduw9y5SOT";
        const redirectUri = `${cleanOrigin}/auth/callback`;
        const stateObj = { origin: cleanOrigin, provider: "github", ts: Date.now() };
        const stateStr = encodeURIComponent(JSON.stringify(stateObj));
        window.location.href = `https://github.com/login/oauth/authorize?client_id=${encodeURIComponent(netlifyClientId)}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=read:user%20user:email&state=${stateStr}`;
      }
    }"""

html = re.sub(old_gh_login_pattern, new_gh_login, html, flags=re.DOTALL)
print("5. Updated loginWithGitHub with Dual-Client + Netlify Forwarding Bridge.")

# Also update the /auth/callback handler to forward from Netlify to Pages.dev if origin matches
callback_pattern = r'if \(urlParams\.has\(\'code\'\)\)\s*\{.*?(?=window\.FloodConfig\.fetchApi\(\'AUTH_OAUTH_EXCHANGE\')'
new_callback_head = """if (urlParams.has('code')) {
        const oauthCode = urlParams.get('code');
        const stateRaw = urlParams.get('state');
        let oauthProvider = 'google';
        let returnOrigin = null;
        try {
          if (stateRaw) {
            const parsed = JSON.parse(decodeURIComponent(stateRaw));
            if (parsed.provider) oauthProvider = parsed.provider;
            if (parsed.origin) returnOrigin = parsed.origin;
          }
        } catch {}

        const cleanRootOrigin = window.location.origin.replace(/\\/+$/, '');

        // If returned to Netlify but state says origin is pages.dev, forward to pages.dev immediately:
        if (returnOrigin && returnOrigin !== cleanRootOrigin && returnOrigin.includes('pages.dev')) {
          window.location.href = `${returnOrigin}/auth/callback?code=${encodeURIComponent(oauthCode)}&state=${encodeURIComponent(stateRaw || '')}`;
          return;
        }

        switchView('auth');
        const status = document.getElementById('authStatusMsg');
        if (status) status.innerHTML = `<span style="color:var(--c-accent);">Authenticating ${oauthProvider === 'github' ? 'GitHub' : 'Google'} credentials with Cloudflare Edge...</span>`;

        // Match redirect_uri exactly to what was passed to GitHub authorize
        const exchangeRedirectUri = (returnOrigin && returnOrigin.includes('pages.dev') && !window.FLOODLOCK_GH_CLIENT_ID_PAGES)
          ? 'https://metoflood.netlify.app/auth/callback'
          : `${cleanRootOrigin}/auth/callback`;

        """

html = re.sub(callback_pattern, new_callback_head, html, flags=re.DOTALL)
html = html.replace("redirect_uri: `${cleanRootOrigin}/auth/callback`", "redirect_uri: exchangeRedirectUri")
print("6. Updated OAuth callback exchange redirect_uri router.")

# ═══════════════════════════════════════════════════════════════════════════
# 6. SWISS DESIGN CONCISE COPY IN VIEW-WELCOME (NO NOVELS, PUNCHY LINES)
# ═══════════════════════════════════════════════════════════════════════════
# Refine Pillar 1, Pillar 2, Pillar 3 to be ultra-concise Swiss style
old_p1 = r'<!-- PILLAR I: WHY -->\s*<div class="tri-pillar-card">.*?</div>\s*</div>'
new_p1 = """<!-- PILLAR I: WHY -->
          <div class="tri-pillar-card">
            <div class="tri-pillar-badge">01 // WHY METEOFLOOD</div>
            <h3 class="tri-pillar-title">Eliminating the 6-Hour Lag</h3>
            <p class="tri-pillar-desc">
              Conventional systems take 6–14 hours on supercomputers. By then, arterial underpasses are submerged. Concurrently, 74% of municipal sirens fire falsely on dry ground, costing $12M per storm in needless city shutdowns.
            </p>
            <div class="tri-pillar-list">
              <div class="tri-pillar-item"><span><strong>12ms Edge Pass:</strong> Solves 2D shallow water physics at CDN edge isolates.</span></div>
              <div class="tri-pillar-item"><span><strong>1.4s Groq Audit:</strong> Adversarial LPU verifies soil headroom before alarms sound.</span></div>
            </div>
          </div>"""

# Replace in tri-pillar-grid
html = re.sub(r'<!-- PILLAR I: WHY -->.*?<!-- PILLAR II: WHO -->', new_p1 + '\n\n          <!-- PILLAR II: WHO -->', html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved all updates to index.html successfully.")
