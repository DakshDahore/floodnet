# /home/daksh/Documents/Projects/floodlock/scripts/apply_ferrari_leather_theme.py
import re

INDEX_PATH = '/home/daksh/Documents/Projects/floodlock/floodlock_frontend/index.html'

with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════════════════════
# 1. NEW LUXURY PALETTE (DARK & LIGHT) IN :root
# ═══════════════════════════════════════════════════════════════════════════
new_root_css = """    :root {
      /* ── The Bespoke Luxury Aesthetic (Dark Mode Default) ──
         Red Ferrari, Tanned Long Leather Coat, Crisp White Shirt, Beige Chinos, Velvet Black Bow */

      --c-bg: #120d09;                      /* Deep Velvet Espresso / Black Bow Lounge */
      --c-surface: #1a130e;                 /* Dark Saddle Leather Surface */
      --c-card-bg: rgba(28, 20, 15, 0.88);  /* Cognac Leather Glass */
      --c-card-border: rgba(196, 126, 75, 0.24); /* Saddle Hand-Stitch Border */
      --c-glass-shine: rgba(255, 255, 255, 0.12);

      /* Typography */
      --c-text-primary: #fcfbf9;            /* Crisp Silk White Shirt */
      --c-text-secondary: #d8c7b5;          /* Tailored Cashmere Beige */
      --c-text-muted: #9a8b7c;              /* Soft Sand Tonal */
      --c-linen: #fcfbf9;
      --c-beige: #d8c7b5;
      --c-obsidian: #120d09;
      --c-umber: #1a130e;

      /* Tanned Leather Coat Spectrum */
      --c-leather-light: #e09f67;           /* Light Tanned Sand */
      --c-leather: #c97a3e;                 /* Rich Tanned Leather Coat */
      --c-leather-deep: #8a481f;            /* Deep Burnished Saddle Leather */
      --c-cognac: #c97a3e;
      --c-cognac-hover: #b46830;
      --c-water: #c97a3e;
      --c-water-glow: rgba(201, 122, 62, 0.4);

      /* Red Ferrari Accent (Rosso Corsa) */
      --c-ferrari: #dc2626;                 /* Rosso Corsa Ferrari Red */
      --c-ferrari-glow: rgba(220, 38, 38, 0.35);
      --c-alert: #dc2626;
      --c-watch: #d97706;
      --c-nominal: #16a34a;

      /* Interactive Button Presets */
      --c-btn-primary-bg: linear-gradient(135deg, #c97a3e 0%, #9a5328 100%);
      --c-btn-primary-text: #ffffff;
      --c-btn-primary-border: #e09f67;
      --c-btn-secondary-bg: rgba(28, 20, 15, 0.7);
      --c-btn-secondary-text: #fcfbf9;
      --c-btn-secondary-border: rgba(196, 126, 75, 0.35);

      /* Glass Sidebar */
      --c-dock-bg: rgba(18, 13, 9, 0.78);
      --c-dock-border: rgba(196, 126, 75, 0.28);
      --c-dock-shadow: rgba(0, 0, 0, 0.85);

      --font-display: 'Instrument Serif', Georgia, serif;
      --font-sans: 'Plus Jakarta Sans', -apple-system, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    [data-theme="light"] {
      /* ── The Bespoke Luxury Aesthetic (Light Mode) ──
         Crisp Silk White Shirt, Tailored Beige Chinos, Saddle Tanned Leather, Rosso Corsa Highlight */

      --c-bg: #f7f4ee;                      /* Tailored Warm Cashmere Beige & Italian Linen */
      --c-surface: #ffffff;                 /* Crisp Silk White Shirt */
      --c-card-bg: rgba(255, 255, 255, 0.96); /* Crisp White Glass */
      --c-card-border: rgba(154, 83, 40, 0.2); /* Hand-Stitched Saddle Leather Border */
      --c-glass-shine: rgba(255, 255, 255, 0.95);

      /* Typography (Black Bow & Deep Espresso — Flawless High Contrast!) */
      --c-text-primary: #18110b;            /* Deep Tuxedo Espresso Black Bow */
      --c-text-secondary: #4a382c;          /* Tailored Saddle Brown */
      --c-text-muted: #7d6858;              /* Muted Warm Tan */
      --c-linen: #18110b;
      --c-beige: #4a382c;
      --c-obsidian: #eae0d5;
      --c-umber: #dfd3c3;

      /* Tanned Leather Coat Spectrum */
      --c-leather-light: #9a5328;
      --c-leather: #8c471e;
      --c-leather-deep: #693211;
      --c-cognac: #8c471e;
      --c-cognac-hover: #753915;
      --c-water: #8c471e;
      --c-water-glow: rgba(140, 71, 30, 0.35);

      /* Red Ferrari Accent */
      --c-ferrari: #dc2626;
      --c-ferrari-glow: rgba(220, 38, 38, 0.25);
      --c-alert: #dc2626;
      --c-watch: #d97706;
      --c-nominal: #16a34a;

      /* Interactive Button Presets */
      --c-btn-primary-bg: linear-gradient(135deg, #9a5328 0%, #7c3f1a 100%);
      --c-btn-primary-text: #ffffff;
      --c-btn-primary-border: #693211;
      --c-btn-secondary-bg: #ffffff;
      --c-btn-secondary-text: #18110b;
      --c-btn-secondary-border: rgba(154, 83, 40, 0.35);

      /* Glass Sidebar */
      --c-dock-bg: rgba(255, 255, 255, 0.88);
      --c-dock-border: rgba(154, 83, 40, 0.25);
      --c-dock-shadow: rgba(100, 70, 50, 0.12);
    }"""

# Replace :root and [data-theme="light"] and [data-theme="cyber"]
pos_root = html.find('    :root {')
pos_cyber_end = html.find('* { box-sizing: border-box;', pos_root)

if pos_root != -1 and pos_cyber_end != -1:
    html = html[:pos_root] + new_root_css + '\n\n    ' + html[pos_cyber_end:]
    print("Luxury Ferrari/Leather :root and light theme injected!")
else:
    print("ERROR finding :root block markers:", pos_root, pos_cyber_end)

# ═══════════════════════════════════════════════════════════════════════════
# 2. UPGRADE SIDEBAR & COMPONENT CSS FOR DUAL THEMES + LESS FILLED SPACING
# ═══════════════════════════════════════════════════════════════════════════
new_components_css = """    /* ══════════════════════════════════════════════════════════════════
       BESPOKE LUXURY SIDEBAR & COMPONENT ARCHITECTURE
       ══════════════════════════════════════════════════════════════════ */
    .water-sidebar {
      position: fixed;
      left: 1.8rem;
      top: 50%;
      transform: translateY(-50%);
      z-index: 1000;
      background: var(--c-dock-bg);
      backdrop-filter: blur(40px) saturate(200%);
      -webkit-backdrop-filter: blur(40px) saturate(200%);
      border: 1px solid var(--c-dock-border);
      box-shadow:
        inset 0 1.5px 2px var(--c-glass-shine),
        0 25px 60px var(--c-dock-shadow);
      border-radius: 40px;
      padding: 0.9rem 0.65rem;
      width: 68px;
      transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }
    .water-sidebar:hover, .water-sidebar.proximity-expanded {
      width: 240px;
      border-color: var(--c-leather);
      box-shadow:
        inset 0 1.5px 2px var(--c-glass-shine),
        0 30px 80px var(--c-dock-shadow),
        0 0 35px var(--c-ferrari-glow);
    }
    .water-dock-list {
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
      width: 100%;
    }
    .water-dock-item {
      display: flex;
      align-items: center;
      gap: 1.1rem;
      padding: 0.8rem 0.95rem;
      border-radius: 26px;
      color: var(--c-text-secondary);
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 500;
      white-space: nowrap;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.26s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
    }
    .water-sidebar:hover .water-dock-item:not(:hover),
    .water-sidebar.proximity-expanded .water-dock-item:not(:hover) {
      opacity: 0.52;
      transform: scale(0.97);
      filter: blur(0.3px);
    }
    .water-dock-item:hover {
      opacity: 1 !important;
      transform: scale(1.05) translateX(6px) !important;
      filter: none !important;
      background: rgba(201, 122, 62, 0.16) !important;
      border-color: var(--c-leather) !important;
      color: var(--c-text-primary) !important;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.3), inset 0 1px 1px var(--c-glass-shine) !important;
    }
    .water-dock-item::after {
      content: '→';
      font-family: var(--font-mono);
      font-size: 0.76rem;
      font-weight: 700;
      color: var(--c-leather);
      position: absolute;
      right: 14px;
      opacity: 0;
      transform: translateX(-6px);
      transition: opacity 0.2s, transform 0.2s;
    }
    .water-sidebar:hover .water-dock-item:hover::after,
    .water-sidebar.proximity-expanded .water-dock-item:hover::after {
      opacity: 1;
      transform: translateX(0);
    }
    .water-dock-item.active {
      opacity: 1 !important;
      background: linear-gradient(135deg, rgba(201, 122, 62, 0.35) 0%, rgba(220, 38, 38, 0.22) 100%) !important;
      border: 1px solid var(--c-leather) !important;
      color: var(--c-text-primary) !important;
      font-weight: 700;
      box-shadow: 0 4px 18px rgba(180, 100, 50, 0.25), inset 0 1px 0 var(--c-glass-shine) !important;
      filter: none !important;
    }
    .water-dock-item.active .dock-icon {
      color: var(--c-leather-light);
      filter: drop-shadow(0 0 10px rgba(220, 38, 38, 0.7));
    }
    .water-dock-item:hover .dock-icon {
      transform: scale(1.2) rotate(-5deg);
      filter: drop-shadow(0 0 10px var(--c-leather));
    }
    .dock-icon {
      font-size: 1.25rem;
      display: flex;
      align-items: center;
      justify-content: center;
      min-width: 28px;
      transition: transform 0.25s, filter 0.25s;
    }
    .dock-label {
      opacity: 0;
      transform: translateX(-10px);
      transition: opacity 0.25s ease, transform 0.25s ease;
      font-family: var(--font-sans);
      letter-spacing: -0.01em;
      color: var(--c-text-primary);
    }
    .water-sidebar:hover .dock-label, .water-sidebar.proximity-expanded .dock-label {
      opacity: 1;
      transform: translateX(0);
    }

    /* ── Less Filled, Highly Breathable Spacing ── */
    .hero-cinematic {
      text-align: center;
      padding: 5.5rem 2rem 4rem;
      max-width: 1040px;
      margin: 0 auto;
      position: relative;
    }
    .hero-title-giant {
      font-family: var(--font-sans);
      font-size: clamp(3rem, 7vw, 5.4rem);
      font-weight: 800;
      line-height: 1.08;
      letter-spacing: -0.035em;
      margin-bottom: 1.25rem;
      color: var(--c-text-primary);
    }
    .hero-title-giant span.gradient-cyan {
      background: linear-gradient(135deg, var(--c-leather-light) 0%, var(--c-leather) 50%, var(--c-ferrari) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .hero-subtitle-lead {
      font-size: 1.05rem;
      color: var(--c-text-secondary);
      max-width: 680px;
      margin: 0 auto 2.2rem;
      line-height: 1.7;
    }
    .chapter-eyebrow {
      font-family: var(--font-mono);
      font-size: 0.76rem;
      color: var(--c-leather);
      letter-spacing: 0.16em;
      text-transform: uppercase;
      font-weight: 700;
      margin-bottom: 0.75rem;
    }
    .chapter-heading-giant {
      font-family: var(--font-sans);
      font-size: clamp(1.9rem, 4vw, 2.8rem);
      font-weight: 800;
      color: var(--c-text-primary);
      line-height: 1.18;
      letter-spacing: -0.025em;
      margin-bottom: 0.75rem;
    }
    .chapter-lead-text {
      font-size: 1rem;
      color: var(--c-text-secondary);
      line-height: 1.68;
      max-width: 720px;
      margin-bottom: 2rem;
    }

    /* ── Theme-Aware Button Architecture ── */
    .btn-keynote-primary {
      display: inline-flex;
      align-items: center;
      gap: 0.65rem;
      background: var(--c-btn-primary-bg);
      color: var(--c-btn-primary-text);
      font-weight: 700;
      font-size: 0.94rem;
      padding: 0.85rem 1.9rem;
      border-radius: 999px;
      border: 1px solid var(--c-btn-primary-border);
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 8px 25px rgba(154, 83, 40, 0.25);
    }
    .btn-keynote-primary:hover {
      transform: translateY(-2px) scale(1.02);
      box-shadow: 0 14px 40px var(--c-ferrari-glow);
    }
    .btn-keynote-secondary {
      display: inline-flex;
      align-items: center;
      gap: 0.65rem;
      background: var(--c-btn-secondary-bg);
      color: var(--c-btn-secondary-text);
      font-weight: 600;
      font-size: 0.94rem;
      padding: 0.85rem 1.9rem;
      border-radius: 999px;
      border: 1px solid var(--c-btn-secondary-border);
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .btn-keynote-secondary:hover {
      transform: translateY(-2px);
      border-color: var(--c-leather);
    }
    .btn-water {
      background: var(--c-btn-primary-bg);
      color: #ffffff;
      border: 1px solid var(--c-btn-primary-border);
      padding: 0.75rem 1.5rem;
      border-radius: 999px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.25s;
      box-shadow: 0 4px 16px rgba(154, 83, 40, 0.2);
    }
    .btn-water:hover {
      box-shadow: 0 0 20px var(--c-ferrari-glow);
      transform: translateY(-2px);
    }

    /* ── Cards & Panels ── */
    .card-luxury {
      background: var(--c-card-bg);
      border: 1px solid var(--c-card-border);
      border-radius: 22px;
      padding: 2.2rem;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25);
      backdrop-filter: blur(24px);
      color: var(--c-text-primary);
    }
    .tri-pillar-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.6rem;
      margin: 2.8rem 0 4.5rem;
    }
    @media (max-width: 900px) {
      .tri-pillar-grid { grid-template-columns: 1fr; }
    }
    .tri-pillar-card {
      background: var(--c-card-bg);
      border: 1px solid var(--c-card-border);
      border-radius: 20px;
      padding: 1.8rem 1.6rem;
      display: flex;
      flex-direction: column;
      box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
      transition: transform 0.25s, border-color 0.25s;
    }
    .tri-pillar-card:hover {
      transform: translateY(-4px);
      border-color: var(--c-leather);
    }
    .tri-pillar-badge {
      font-family: var(--font-mono);
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--c-leather);
      background: rgba(201, 122, 62, 0.12);
      border: 1px solid var(--c-card-border);
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
      width: fit-content;
      margin-bottom: 0.9rem;
    }
    .tri-pillar-title {
      font-family: var(--font-sans);
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--c-text-primary);
      line-height: 1.25;
      margin-bottom: 0.75rem;
    }
    .tri-pillar-desc {
      font-size: 0.9rem;
      color: var(--c-text-secondary);
      line-height: 1.6;
      margin-bottom: 1.1rem;
    }
    .tri-pillar-list {
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
      border-top: 1px solid var(--c-card-border);
      padding-top: 1rem;
      margin-top: auto;
    }
    .tri-pillar-item {
      font-size: 0.86rem;
      color: var(--c-text-secondary);
      line-height: 1.5;
      display: flex;
      gap: 0.5rem;
    }
    .tri-pillar-item::before {
      content: '▸';
      color: var(--c-leather);
      font-weight: 700;
      flex-shrink: 0;
    }
    .tri-pillar-item strong {
      color: var(--c-text-primary);
    }

    /* ── Pipeline Grid ── */
    .pipeline-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.2rem;
      margin: 2.5rem 0 4.5rem;
    }
    @media (max-width: 900px) {
      .pipeline-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 600px) {
      .pipeline-grid { grid-template-columns: 1fr; }
    }
    .pipeline-step-card {
      background: var(--c-card-bg);
      border: 1px solid var(--c-card-border);
      border-radius: 16px;
      padding: 1.4rem 1.25rem;
      transition: all 0.25s ease;
    }
    .pipeline-step-card:hover {
      border-color: var(--c-leather);
      transform: translateY(-3px);
    }
    .pipeline-step-num {
      font-family: var(--font-mono);
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--c-leather);
      margin-bottom: 0.4rem;
    }
    .pipeline-step-title {
      font-family: var(--font-sans);
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--c-text-primary);
      margin-bottom: 0.4rem;
    }
    .pipeline-step-desc {
      font-size: 0.84rem;
      color: var(--c-text-secondary);
      line-height: 1.55;
    }
    .pipeline-step-badge {
      display: inline-block;
      margin-top: 0.8rem;
      font-family: var(--font-mono);
      font-size: 0.68rem;
      color: var(--c-leather);
      background: rgba(201, 122, 62, 0.1);
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
      border: 1px solid var(--c-card-border);
    }

    /* ── Sovereign Leadership Banner ── */
    .sovereign-banner {
      background: var(--c-card-bg);
      border: 1px solid var(--c-card-border);
      border-radius: 22px;
      padding: 2.5rem 2.2rem;
      margin: 4.5rem 0 3.5rem;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
      position: relative;
    }
    .sovereign-banner::after {
      content: '';
      position: absolute;
      top: -60px; right: -60px;
      width: 240px; height: 240px;
      background: radial-gradient(circle, var(--c-ferrari-glow) 0%, transparent 70%);
      pointer-events: none;
    }

    /* Header & Nav */
    header {
      background: var(--c-card-bg) !important;
      border-bottom: 1px solid var(--c-card-border) !important;
    }
    .brand { color: var(--c-text-primary) !important; }
    .brand span { color: var(--c-leather) !important; }
"""

# Replace the previous sidebar and component CSS
pos_comp_start = html.find('    /* ══════════════════════════════════════════════════════════════════\n       APPLE LIQUID GLASSMORPHIC SIDEBAR')
pos_comp_end = html.find('    /* ══════════════════════════════════════════════════════════════════\n       MAIN WRAPPER & SECTIONS')

if pos_comp_start != -1 and pos_comp_end != -1:
    html = html[:pos_comp_start] + new_components_css + '\n\n' + html[pos_comp_end:]
    print("New luxury components CSS replaced successfully!")
else:
    print("ERROR finding component CSS markers:", pos_comp_start, pos_comp_end)

# ═══════════════════════════════════════════════════════════════════════════
# 3. REMOVE LOGOUT BUTTON FROM DOCK (KEEP IN ACCOUNT VIEW)
# ═══════════════════════════════════════════════════════════════════════════
old_logout_dock = """      <div class="water-dock-item" onclick="logoutSession()">
        <span class="dock-icon">🚪</span>
        <span class="dock-label">Log Out</span>
      </div>"""

if old_logout_dock in html:
    html = html.replace(old_logout_dock, '')
    print("Removed logout button from water-sidebar dock!")
else:
    # Try regex match
    html = re.sub(r'<div class="water-dock-item" onclick="logoutSession\(\)">[\s\S]*?</div>', '', html, count=1)
    print("Regex removed logout from dock!")

# ═══════════════════════════════════════════════════════════════════════════
# 4. SETTINGS VIEW: 2 THEMES ONLY (DARK & LIGHT)
# ═══════════════════════════════════════════════════════════════════════════
old_theme_buttons = """              <button onclick="setTheme('dark')" class="btn-water" style="flex: 1;">Savile Row (Dark)</button>
              <button onclick="setTheme('light')" class="btn-water" style="flex: 1;">Crisp Linen (Light)</button>
              <button onclick="setTheme('cyber')" class="btn-water" style="flex: 1;">Cyber Basin (Ocean)</button>"""

new_theme_buttons = """              <button onclick="setTheme('dark')" class="btn-keynote-secondary" id="themeBtnDark" style="flex: 1; justify-content: center;">🕶️ Tanned Leather &amp; Espresso (Dark)</button>
              <button onclick="setTheme('light')" class="btn-keynote-secondary" id="themeBtnLight" style="flex: 1; justify-content: center;">👔 Italian Linen &amp; Camel (Light)</button>"""

if old_theme_buttons in html:
    html = html.replace(old_theme_buttons, new_theme_buttons)
    print("Replaced 3 theme buttons with 2 luxury theme buttons!")
else:
    html = re.sub(r'<div style="display: flex; gap: 0.75rem;">[\s\S]*?setTheme\(\'cyber\'\)[\s\S]*?</div>',
                  f'<div style="display: flex; gap: 0.75rem;">\n{new_theme_buttons}\n            </div>', html)
    print("Regex replaced theme buttons!")

# Update setTheme function to enforce 2 modes
new_set_theme_fn = """    function setTheme(th) {
      const mode = (th === 'light') ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', mode);
      localStorage.setItem('floodlock_theme', mode);
      showFloatingToast('Display theme set to ' + (mode === 'light' ? 'Italian Linen & Camel (Light)' : 'Tanned Leather & Espresso (Dark)'));
    }"""

html = re.sub(r'function setTheme\(th\)\s*\{[\s\S]*?\}', new_set_theme_fn, html)

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("Ferrari / Tanned Leather luxury theme applied successfully!")
