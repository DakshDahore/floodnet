# /home/daksh/Documents/Projects/floodlock/scripts/apply_apple_glass_sidebar.py
import re

INDEX_PATH = '/home/daksh/Documents/Projects/floodlock/floodlock_frontend/index.html'

with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════════════════════
# 1. UPGRADE :root PALETTE (2 CLASSY PRIMARIES + ACCENT HIGHLIGHT)
# ═══════════════════════════════════════════════════════════════════════════
new_root_palette = """    :root {
      /* ── Primary 1: Deep Cosmic Obsidian / Midnight Navy ── */
      --c-obsidian: #050810;
      --c-umber: #090e1a;
      --c-navy-deep: #050810;
      --c-navy-mid: #0b1325;
      --c-navy-surface: #101a33;

      /* ── Primary 2: Arctic Cyan & Electric Cerulean Spectrum ── */
      --c-cyan-deep: #0369a1;
      --c-cyan-base: #0ea5e9;
      --c-cyan-bright: #38bdf8;
      --c-cyan-frost: #7dd3fc;
      --c-cyan-ice: #e0f2fe;
      --c-cyan-glow: rgba(56, 189, 248, 0.35);
      --c-water: #0ea5e9;
      --c-water-glow: rgba(14, 165, 233, 0.45);

      /* ── Highlight Accent: Solar Amber / Cognac (Subtle Click Targets) ── */
      --c-cognac: #f59e0b;
      --c-cognac-hover: #d97706;
      --c-amber-bright: #fbbf24;
      --c-amber-glow: rgba(245, 158, 11, 0.35);
      --c-amber-subtle: rgba(245, 158, 11, 0.12);

      /* ── Semantic Threat Colors ── */
      --c-alert: #ef4444;
      --c-watch: #f59e0b;
      --c-nominal: #10b981;

      /* ── Glassmorphism Surfaces ── */
      --c-bg: #050810;
      --c-card-bg: rgba(9, 14, 26, 0.78);
      --c-card-border: rgba(56, 189, 248, 0.18);
      --c-glass-shine: rgba(255, 255, 255, 0.12);
      --c-linen: #f8fafc;
      --c-text-muted: #94a3b8;

      --font-display: 'Instrument Serif', Georgia, serif;
      --font-sans: 'Plus Jakarta Sans', -apple-system, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }"""

pos_root_start = html.find('    :root {')
pos_root_end = html.find('    }', pos_root_start) + 5

if pos_root_start != -1 and pos_root_end != -1:
    html = html[:pos_root_start] + new_root_palette + html[pos_root_end:]
    print("New classy 2-primary + highlight palette injected into :root!")
else:
    print("ERROR finding :root markers:", pos_root_start, pos_root_end)

# ═══════════════════════════════════════════════════════════════════════════
# 2. APPLE GLASSMORPHIC ANIMATED SIDEBAR CSS
# ═══════════════════════════════════════════════════════════════════════════
new_sidebar_css = """    /* ══════════════════════════════════════════════════════════════════
       APPLE LIQUID GLASSMORPHIC SIDEBAR & DYNAMIC DOCK
       ══════════════════════════════════════════════════════════════════ */
    .water-sidebar {
      position: fixed;
      left: 1.5rem;
      top: 50%;
      transform: translateY(-50%);
      z-index: 1000;
      background: rgba(7, 12, 24, 0.62);
      backdrop-filter: blur(40px) saturate(220%);
      -webkit-backdrop-filter: blur(40px) saturate(220%);
      border: 1px solid rgba(255, 255, 255, 0.14);
      box-shadow:
        inset 0 1.5px 2px rgba(255, 255, 255, 0.32),
        inset 0 -1px 2px rgba(0, 0, 0, 0.5),
        0 25px 60px rgba(0, 0, 0, 0.8),
        0 0 35px rgba(14, 165, 233, 0.16);
      border-radius: 40px;
      padding: 0.85rem 0.6rem;
      width: 68px;
      transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      gap: 0.55rem;
    }
    .water-sidebar:hover, .water-sidebar.proximity-expanded {
      width: 236px;
      border-color: rgba(56, 189, 248, 0.45);
      box-shadow:
        inset 0 1.5px 2px rgba(255, 255, 255, 0.4),
        0 30px 75px rgba(0, 0, 0, 0.85),
        0 0 45px rgba(56, 189, 248, 0.28);
    }

    /* Dock Nav Container */
    .water-dock-list {
      display: flex;
      flex-direction: column;
      gap: 0.55rem;
      width: 100%;
    }

    /* Individual Glass Dock Item */
    .water-dock-item {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 0.75rem 0.85rem;
      border-radius: 26px;
      color: #94a3b8;
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 500;
      white-space: nowrap;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.26s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
    }

    /* "Fluid Around It Gets Away" Sibling Dimming */
    .water-sidebar:hover .water-dock-item:not(:hover),
    .water-sidebar.proximity-expanded .water-dock-item:not(:hover) {
      opacity: 0.52;
      transform: scale(0.97);
      filter: blur(0.3px);
    }

    /* Hovered Item: Expands, Swells & Says "Click Me" */
    .water-dock-item:hover {
      opacity: 1 !important;
      transform: scale(1.05) translateX(6px) !important;
      filter: none !important;
      background: radial-gradient(circle at 25% 50%, rgba(56, 189, 248, 0.24) 0%, rgba(14, 165, 233, 0.1) 100%) !important;
      border-color: rgba(56, 189, 248, 0.5) !important;
      color: #ffffff !important;
      box-shadow:
        0 10px 24px rgba(0, 0, 0, 0.5),
        0 0 20px rgba(56, 189, 248, 0.35),
        inset 0 1px 1px rgba(255, 255, 255, 0.4) !important;
    }

    /* Tactile "Click Me" Arrow Indicator */
    .water-dock-item::after {
      content: '→';
      font-family: var(--font-mono);
      font-size: 0.76rem;
      font-weight: 700;
      color: #38bdf8;
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

    /* Active Selected State */
    .water-dock-item.active {
      opacity: 1 !important;
      background: linear-gradient(135deg, rgba(14, 165, 233, 0.3) 0%, rgba(245, 158, 11, 0.18) 100%) !important;
      border: 1px solid rgba(56, 189, 248, 0.55) !important;
      color: #ffffff !important;
      font-weight: 700;
      box-shadow: 0 4px 18px rgba(14, 165, 233, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
      filter: none !important;
    }
    .water-dock-item.active .dock-icon {
      color: #38bdf8;
      filter: drop-shadow(0 0 10px rgba(56, 189, 248, 0.9));
    }
    .water-dock-item:hover .dock-icon {
      transform: scale(1.2) rotate(-5deg);
      filter: drop-shadow(0 0 10px #38bdf8);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), filter 0.25s ease;
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
    }
    .water-sidebar:hover .dock-label, .water-sidebar.proximity-expanded .dock-label {
      opacity: 1;
      transform: translateX(0);
    }

    /* Highlight Accent on Click Buttons */
    .btn-water {
      background: linear-gradient(135deg, rgba(14, 165, 233, 0.25) 0%, rgba(56, 189, 248, 0.38) 100%);
      border: 1px solid rgba(56, 189, 248, 0.5);
      color: #f0f9ff;
      padding: 0.8rem 1.6rem;
      border-radius: 999px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.25s;
      box-shadow: 0 4px 16px rgba(14, 165, 233, 0.2);
    }
    .btn-water:hover {
      background: linear-gradient(135deg, rgba(14, 165, 233, 0.4) 0%, rgba(56, 189, 248, 0.6) 100%);
      box-shadow: 0 0 24px rgba(56, 189, 248, 0.45);
      transform: translateY(-2px);
    }
    .btn-keynote-primary {
      display: inline-flex;
      align-items: center;
      gap: 0.65rem;
      background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
      color: #070a12;
      font-weight: 700;
      font-size: 0.96rem;
      padding: 0.85rem 1.85rem;
      border-radius: 999px;
      border: 1px solid rgba(255, 255, 255, 0.9);
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 8px 25px rgba(255, 255, 255, 0.16), 0 0 15px rgba(56, 189, 248, 0.2);
    }
    .btn-keynote-primary:hover {
      transform: translateY(-2px) scale(1.02);
      box-shadow: 0 14px 40px rgba(56, 189, 248, 0.45), 0 0 20px rgba(245, 158, 11, 0.25);
      background: #ffffff;
    }"""

# Replace old sidebar CSS
pos_sb_start = html.find('    /* ══════════════════════════════════════════════════════════════════\n       WATERY FLUID SIDEBAR')
if pos_sb_start == -1:
    pos_sb_start = html.find('.water-sidebar {')
    pos_sb_start = html.rfind('/*', 0, pos_sb_start)

pos_sb_end = html.find('    /* ══════════════════════════════════════════════════════════════════\n       MAIN WRAPPER & SECTIONS', pos_sb_start)

if pos_sb_start != -1 and pos_sb_end != -1:
    html = html[:pos_sb_start] + new_sidebar_css + '\n\n' + html[pos_sb_end:]
    print("New Apple Glassmorphic animated sidebar CSS injected successfully!")
else:
    print("ERROR finding sidebar CSS markers:", pos_sb_start, pos_sb_end)

# ═══════════════════════════════════════════════════════════════════════════
# 3. ENHANCE SIDEBAR PROXIMITY SENSING & TACTILE AUDIO IN JAVASCRIPT
# ═══════════════════════════════════════════════════════════════════════════
new_proximity_js = """    // ── Apple Glassmorphic Sidebar Proximity & Magnetic Controller ──
    let isSidebarNearby = false;
    document.addEventListener('mousemove', (e) => {
      const sidebar = document.getElementById('waterSidebar');
      if (!sidebar) return;

      // Hysteresis window: open at <= 170px, close only when > 260px
      if (e.clientX <= 170) {
        if (!isSidebarNearby) {
          isSidebarNearby = true;
          sidebar.classList.add('proximity-expanded');
          if (typeof audioEngine !== 'undefined') audioEngine.playDrop();
        }
      } else if (e.clientX > 260) {
        if (isSidebarNearby) {
          isSidebarNearby = false;
          sidebar.classList.remove('proximity-expanded');
        }
      }
    });

    // Sound and hover trigger on dock items
    document.addEventListener('DOMContentLoaded', () => {
      document.querySelectorAll('.water-dock-item').forEach(item => {
        item.addEventListener('mouseenter', () => {
          if (typeof audioEngine !== 'undefined') audioEngine.playDrop();
        });
      });
    });"""

pos_prox_start = html.find("document.addEventListener('mousemove', (e) => {")
pos_prox_end = html.find("/* ══════════════════════════════════════════════════════════════════\n       8. AUTHENTICATION & SESSION MANAGEMENT", pos_prox_start)

if pos_prox_start != -1 and pos_prox_end != -1:
    html = html[:pos_prox_start] + new_proximity_js + '\n\n    ' + html[pos_prox_end:]
    print("New proximity sensing JS injected successfully!")
else:
    print("ERROR finding proximity JS markers:", pos_prox_start, pos_prox_end)

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("Apple Glass & Color Gridding upgrade complete!")

