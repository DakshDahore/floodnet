import re

html_path = '/home/daksh/Documents/Projects/floodlock/floodlock_frontend/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Google Fonts Link
old_font_link = re.search(r'<link href="https://fonts\.googleapis\.com/css2\?family=Instrument\+Serif[^"]+" rel="stylesheet">', content)
new_font_link = '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,400;1,600&family=Montserrat:wght@500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,400;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">'

if old_font_link:
    content = content.replace(old_font_link.group(0), new_font_link)
    print("Updated Google Fonts link.")

# 2. Update :root and [data-theme="light"]
root_pattern = r':root\s*\{.*?\n    \}'
light_pattern = r'\[data-theme="light"\]\s*\{.*?\n    \}'

new_root = """:root {
      /* ══════════════════════════════════════════════════════════════════════
         DARK THEME: ONYX TRENCH & ANTIQUE GOLD (60 - 30 - 10 RULE)
         60% Canvas / Main: #121212 (Onyx Trench)
         30% Structural / Surfaces: #262626 (Slate Wool)
         10% High-Intent Accents & Focus: #B45309 (Antique Gold)
         ══════════════════════════════════════════════════════════════════════ */
      --c-bg: #121212;                           /* 60% Onyx Trench Canvas */
      --c-canvas: #121212;
      --c-surface: #1e1e1e;
      --c-card-bg: rgba(38, 38, 38, 0.94);       /* 30% Slate Wool Surfaces */
      --c-card-border: rgba(180, 83, 9, 0.26);   /* Antique Gold Fine Edge */
      --c-glass-shine: rgba(255, 255, 255, 0.08);

      /* Typography */
      --c-text-primary: #f5f5f5;                 /* Crisp Silk Ivory */
      --c-text-secondary: #d4d4d4;               /* Tailored Slate */
      --c-text-muted: #a3a3a3;                   /* Muted Wool */
      --c-linen: #f5f5f5;
      --c-beige: #d4d4d4;
      --c-obsidian: #121212;
      --c-umber: #1e1e1e;

      /* 10% Antique Gold & Leather Spectrum */
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
      --c-dock-bg: rgba(26, 26, 26, 0.88);
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

new_light = """[data-theme="light"] {
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
      --c-card-border: rgba(69, 26, 3, 0.20);    /* Espresso Roast Edge */
      --c-glass-shine: rgba(255, 255, 255, 0.7);

      /* Typography (Deep Espresso Roast — 100% Legibility!) */
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
      --c-dock-bg: rgba(230, 216, 195, 0.94);
      --c-dock-border: rgba(69, 26, 3, 0.25);
      --c-dock-shadow: rgba(69, 26, 3, 0.18);
    }"""

content = re.sub(root_pattern, new_root, content, flags=re.DOTALL)
content = re.sub(light_pattern, new_light, content, flags=re.DOTALL)
print("Updated :root and [data-theme='light'] color engines.")

# 3. Add Swiss Typography CSS Rules & Smooth Scroll Reveal without blur
swiss_typography_css = """
    /* ══════════════════════════════════════════════════════════════════════
       SWISS INTERNATIONAL TYPOGRAPHY & BESPOKE OLD MONEY SYSTEM
       ══════════════════════════════════════════════════════════════════════ */
    .hero-title-giant {
      font-family: var(--font-hero) !important;
      font-size: clamp(2.4rem, 5.2vw, 4.4rem);
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      line-height: 1.1;
      margin-bottom: 1rem;
    }

    .brand-logo-text {
      font-family: var(--font-hero) !important;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .chapter-eyebrow, .hero-badge-pill, .tri-pillar-badge, .pipeline-step-badge, .tensor-chip {
      font-family: var(--font-btn) !important;
      font-size: 0.72rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-weight: 700;
    }

    .chapter-heading-giant, h1, h2, h3, .tri-pillar-title, .pipeline-step-title {
      font-family: var(--font-editorial) !important;
      font-weight: 700;
      letter-spacing: -0.01em;
    }

    .hero-subtitle-lead, .chapter-lead-text, .pull-quote {
      font-family: var(--font-subheading) !important;
      font-size: 1.25rem;
      line-height: 1.6;
    }

    body, p, span, div, input, textarea, select {
      font-family: var(--font-body);
    }

    button, .btn-keynote-primary, .btn-keynote-secondary, .btn-magnetic, .btn-water, .water-dock-item {
      font-family: var(--font-btn) !important;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 600;
    }

    code, pre, .mono, [id*="quota"], [id*="status"], .hero-stat-num {
      font-family: var(--font-mono) !important;
    }

    /* ── Smooth Hardware-Accelerated Story Transitions (Zero Blur / Zero Hang) ── */
    .scroll-reveal {
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
    }
"""

# Replace or inject into CSS block
if '.hero-title-giant {' in content:
    content = re.sub(r'/\* ── Luxury Hero Cinematic Styling ── \*/.*?(?=\.hero-cinematic \{)', '/* ── Luxury Hero Cinematic Styling ── */\n' + swiss_typography_css, content, flags=re.DOTALL)
    print("Injected Swiss typography CSS rules.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved index.html successfully.")
