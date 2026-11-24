# /home/daksh/Documents/Projects/floodlock/scripts/fix_all_light_mode_styles.py
import re

INDEX_PATH = '/home/daksh/Documents/Projects/floodlock/floodlock_frontend/index.html'

with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════════════════════
# 1. LIGHT MODE COMPREHENSIVE CSS FIXES
# ═══════════════════════════════════════════════════════════════════════════
light_mode_css = """
    /* ══════════════════════════════════════════════════════════════════
       FLAWLESS LIGHT MODE COMPREHENSIVE FIXES (NO BROKEN BUTTONS/TEXT)
       ══════════════════════════════════════════════════════════════════ */
    [data-theme="light"] body {
      background-color: var(--c-bg) !important;
      color: var(--c-text-primary) !important;
    }

    [data-theme="light"] .card-luxury,
    [data-theme="light"] .tri-pillar-card,
    [data-theme="light"] .pipeline-step-card,
    [data-theme="light"] .sovereign-banner,
    [data-theme="light"] .groq-testbench-card {
      background: #ffffff !important;
      border: 1px solid rgba(154, 83, 40, 0.22) !important;
      box-shadow: 0 12px 35px rgba(100, 70, 50, 0.08) !important;
      color: #18110b !important;
    }

    [data-theme="light"] .chapter-heading-giant,
    [data-theme="light"] .tri-pillar-title,
    [data-theme="light"] .pipeline-step-title,
    [data-theme="light"] h1, [data-theme="light"] h2, [data-theme="light"] h3, [data-theme="light"] h4 {
      color: #18110b !important;
    }

    [data-theme="light"] .hero-title-giant {
      background: linear-gradient(180deg, #18110b 20%, #4a382c 70%, #7d6858 100%) !important;
      -webkit-background-clip: text !important;
      -webkit-text-fill-color: transparent !important;
    }

    [data-theme="light"] .hero-subtitle-lead,
    [data-theme="light"] .chapter-lead-text,
    [data-theme="light"] .tri-pillar-desc,
    [data-theme="light"] .pipeline-step-desc,
    [data-theme="light"] p {
      color: #4a382c !important;
    }

    [data-theme="light"] .btn-keynote-primary {
      background: linear-gradient(135deg, #9a5328 0%, #7c3f1a 100%) !important;
      color: #ffffff !important;
      border: 1px solid #693211 !important;
      box-shadow: 0 8px 24px rgba(154, 83, 40, 0.25) !important;
    }

    [data-theme="light"] .btn-keynote-secondary {
      background: #ffffff !important;
      color: #18110b !important;
      border: 1px solid rgba(154, 83, 40, 0.35) !important;
      box-shadow: 0 4px 15px rgba(100, 70, 50, 0.06) !important;
    }

    [data-theme="light"] .btn-water {
      background: linear-gradient(135deg, #9a5328 0%, #7c3f1a 100%) !important;
      color: #ffffff !important;
      border: 1px solid #693211 !important;
    }

    [data-theme="light"] .hero-stat-strip {
      background: #ffffff !important;
      border: 1px solid rgba(154, 83, 40, 0.2) !important;
      box-shadow: 0 10px 30px rgba(100, 70, 50, 0.08) !important;
    }

    [data-theme="light"] .hero-stat-num {
      color: #9a5328 !important;
    }

    [data-theme="light"] .hero-stat-lbl {
      color: #695548 !important;
    }

    [data-theme="light"] .tensor-chip {
      background: rgba(255, 255, 255, 0.95) !important;
      border: 1px solid rgba(154, 83, 40, 0.25) !important;
    }

    [data-theme="light"] .tensor-chip.active {
      background: rgba(154, 83, 40, 0.12) !important;
      border-color: #9a5328 !important;
    }

    [data-theme="light"] .tensor-chip-name {
      color: #18110b !important;
    }

    [data-theme="light"] .tensor-chip-index {
      color: #9a5328 !important;
    }

    [data-theme="light"] .tensor-chip-physics {
      color: #7d6858 !important;
    }

    [data-theme="light"] .hero-badge-pill {
      background: #ffffff !important;
      border: 1px solid rgba(154, 83, 40, 0.25) !important;
      color: #4a382c !important;
      box-shadow: 0 4px 15px rgba(100, 70, 50, 0.08) !important;
    }

    [data-theme="light"] .code-terminal-deck {
      background: #1e1610 !important;
      border: 1px solid rgba(154, 83, 40, 0.3) !important;
    }

    [data-theme="light"] input, [data-theme="light"] textarea, [data-theme="light"] select {
      background: #ffffff !important;
      border: 1px solid rgba(154, 83, 40, 0.3) !important;
      color: #18110b !important;
    }

    [data-theme="light"] .search-trigger-btn {
      background: #ffffff !important;
      border: 1px solid rgba(154, 83, 40, 0.25) !important;
      color: #4a382c !important;
    }

    [data-theme="light"] .water-sidebar {
      background: rgba(255, 255, 255, 0.88) !important;
      border: 1px solid rgba(154, 83, 40, 0.28) !important;
      box-shadow: 0 20px 50px rgba(100, 70, 50, 0.14) !important;
    }

    [data-theme="light"] .water-dock-item {
      color: #4a382c !important;
    }

    [data-theme="light"] .water-dock-item:hover {
      background: rgba(154, 83, 40, 0.12) !important;
      color: #18110b !important;
    }

    [data-theme="light"] .water-dock-item.active {
      background: linear-gradient(135deg, rgba(154, 83, 40, 0.2) 0%, rgba(220, 38, 38, 0.15) 100%) !important;
      border-color: #9a5328 !important;
      color: #18110b !important;
    }
"""

# Inject before </style>
pos_style_end = html.find('</style>')
if pos_style_end != -1:
    html = html[:pos_style_end] + light_mode_css + html[pos_style_end:]
    print("Light mode comprehensive CSS injected!")

# ═══════════════════════════════════════════════════════════════════════════
# 2. REPLACE INLINE HARDCODED WHITE IN VIEW-WELCOME
# ═══════════════════════════════════════════════════════════════════════════
pos1_vw = html.find('<section id="view-welcome"')
pos2_vw = html.find('</section>', pos1_vw)

if pos1_vw != -1 and pos2_vw != -1:
    vw = html[pos1_vw:pos2_vw]
    # Replace #ffffff titles with var(--c-text-primary)
    vw = vw.replace('color: #ffffff;', 'color: var(--c-text-primary);')
    vw = vw.replace('color: #38bdf8;', 'color: var(--c-leather);')
    html = html[:pos1_vw] + vw + html[pos2_vw:]
    print("Cleaned inline hardcoded white/cyan in view-welcome!")

# ═══════════════════════════════════════════════════════════════════════════
# 3. VERIFY LOGOUT IS REMOVED FROM SIDEBAR DOCK
# ═══════════════════════════════════════════════════════════════════════════
html = re.sub(r'<div class="water-dock-item" onclick="logoutSession\(\)">[\s\S]*?</div>', '', html)

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("Light mode and layout breathing room successfully applied!")
