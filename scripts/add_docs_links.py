import re

html_path = '/home/daksh/Documents/Projects/floodlock/floodlock_frontend/index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# ═══════════════════════════════════════════════════════════════════════════
# 1. ADD CSS FOR .btn-docs-header & .docs-callout-banner
# ═══════════════════════════════════════════════════════════════════════════
docs_css = """
    /* ── Bold & Clear Documentation Portal Links ── */
    .btn-docs-header {
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      padding: 0.45rem 1.05rem;
      border-radius: 999px;
      font-family: var(--font-btn) !important;
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      text-decoration: none !important;
      background: var(--c-btn-primary-bg);
      color: var(--c-btn-primary-text) !important;
      border: 1px solid var(--c-btn-primary-border);
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
      white-space: nowrap;
    }
    .btn-docs-header:hover {
      transform: translateY(-2px);
      filter: brightness(1.15);
      box-shadow: 0 8px 24px var(--c-accent-glow);
    }
    @media (max-width: 640px) {
      .btn-docs-header {
        padding: 0.35rem 0.75rem;
        font-size: 0.7rem;
      }
    }

    .docs-callout-banner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1.25rem;
      padding: 1.5rem 1.8rem;
      margin: 2.5rem 0;
      border-radius: 20px;
      background: var(--c-card-bg);
      border: 2px solid var(--c-accent);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }
    [data-theme="light"] .docs-callout-banner {
      background: #E6D8C3 !important;
      border: 2px solid #451A03 !important;
      box-shadow: 0 10px 25px rgba(69, 26, 3, 0.12) !important;
    }
"""

if '.btn-docs-header {' not in html:
    html = html.replace('/* ── Accessible Focus Ring ── */', docs_css + '\n    /* ── Accessible Focus Ring ── */')
    print("1. Injected .btn-docs-header and .docs-callout-banner CSS.")

# ═══════════════════════════════════════════════════════════════════════════
# 2. ADD DOCS BUTTON TO SITE HEADER
# ═══════════════════════════════════════════════════════════════════════════
header_target = '<div class="header-right">'
header_replacement = """<div class="header-right">
      <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="btn-docs-header" title="Official FloodLock Documentation Portal">
        <span>📖</span> <span>DOCS ↗</span>
      </a>"""

if 'class="btn-docs-header"' not in html:
    html = html.replace(header_target, header_replacement, 1)
    print("2. Added Docs button to top site header.")

# ═══════════════════════════════════════════════════════════════════════════
# 3. ADD DOCS ITEM TO WATER SIDEBAR (PRE & POST LOGIN)
# ═══════════════════════════════════════════════════════════════════════════
sidebar_pre_target = """      <div class="water-dock-item active" onclick="switchView('welcome')">
        <span class="dock-icon">🌊</span>
        <span class="dock-label">Intro Story</span>
      </div>"""

sidebar_pre_replacement = """      <div class="water-dock-item active" onclick="switchView('welcome')">
        <span class="dock-icon">🌊</span>
        <span class="dock-label">Intro Story</span>
      </div>
      <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="water-dock-item" style="text-decoration: none; color: inherit;" title="Official FloodLock Documentation">
        <span class="dock-icon">📖</span>
        <span class="dock-label">Docs Portal ↗</span>
      </a>"""

if 'title="Official FloodLock Documentation"' not in html:
    html = html.replace(sidebar_pre_target, sidebar_pre_replacement, 1)

sidebar_post_target = """      <div class="water-dock-item" onclick="switchView('api')">
        <span class="dock-icon">⚡</span>
        <span class="dock-label">API Platform</span>
      </div>"""

sidebar_post_replacement = """      <div class="water-dock-item" onclick="switchView('api')">
        <span class="dock-icon">⚡</span>
        <span class="dock-label">API Platform</span>
      </div>
      <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="water-dock-item" style="text-decoration: none; color: inherit;" title="Official FloodLock Documentation Portal">
        <span class="dock-icon">📖</span>
        <span class="dock-label">Docs Portal ↗</span>
      </a>"""

if 'title="Official FloodLock Documentation Portal"' not in html:
    html = html.replace(sidebar_post_target, sidebar_post_replacement, 1)
    print("3. Added Docs Portal item to proximity sidebar.")

# ═══════════════════════════════════════════════════════════════════════════
# 4. ADD DOCS LINK TO MOBILE NAVIGATION DRAWER
# ═══════════════════════════════════════════════════════════════════════════
mobile_drawer_target = """      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('welcome');">
        <span>🌊</span> <span>Intro Story</span>
      </div>"""

mobile_drawer_replacement = """      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('welcome');">
        <span>🌊</span> <span>Intro Story</span>
      </div>
      <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="mobile-drawer-link" style="text-decoration: none; font-weight: 800; color: var(--c-accent);">
        <span>📖</span> <span>Documentation Portal ↗</span>
      </a>"""

if 'Documentation Portal ↗</span>\n      </a>' not in html:
    html = html.replace(mobile_drawer_target, mobile_drawer_replacement, 1)
    print("4. Added Docs Portal link to mobile drawer.")

# ═══════════════════════════════════════════════════════════════════════════
# 5. ADD BOLD DOCS BUTTON TO HERO CTA GROUP
# ═══════════════════════════════════════════════════════════════════════════
hero_cta_target = """        <div class="hero-cta-group">
          <button class="btn-keynote-primary" onclick="switchView('dashboard')">
            <span>🛰️ Launch Live Tactical Radar</span>
            <span>→</span>
          </button>"""

hero_cta_replacement = """        <div class="hero-cta-group">
          <button class="btn-keynote-primary" onclick="switchView('dashboard')">
            <span>🛰️ Launch Live Tactical Radar</span>
            <span>→</span>
          </button>
          <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="btn-keynote-primary" style="text-decoration: none; font-weight: 800; background: var(--c-leather); border-color: var(--c-leather-light);">
            <span>📖 Official Docs ↗</span>
          </a>"""

if '<span>📖 Official Docs ↗</span>' not in html:
    html = html.replace(hero_cta_target, hero_cta_replacement, 1)
    print("5. Added bold Official Docs button to Hero CTA group.")

# ═══════════════════════════════════════════════════════════════════════════
# 6. ADD PROMINENT "FOR MORE INFO GO TO DOCS" BANNER IN EXECUTIVE BRIEFING
# ═══════════════════════════════════════════════════════════════════════════
exec_briefing_target = '        </div>\n      </div>\n\n      <!-- 3. HOW IT WORKS: 4-STEP PIPELINE -->'

exec_briefing_replacement = """        </div>

        <!-- ── BOLD & CLEAR DOCS CALLOUT BANNER ── -->
        <div class="docs-callout-banner scroll-reveal">
          <div style="max-width: 660px;">
            <div style="font-family: var(--font-btn); font-size: 0.74rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--c-accent); font-weight: 800; margin-bottom: 0.35rem;">
              📚 FOR COMPLETE SYSTEM INFORMATION &amp; RESEARCH SPECIFICATIONS
            </div>
            <h3 style="font-family: var(--font-editorial); font-size: 1.45rem; font-weight: 700; color: var(--c-text-primary); margin-bottom: 0.4rem; line-height: 1.25;">
              Explore the Full MeteoFlood Documentation Portal
            </h3>
            <p style="font-size: 0.92rem; color: var(--c-text-secondary); line-height: 1.55; margin: 0;">
              For mathematical derivations, 2.7M PINN Navier-Stokes equations, GloFAS satellite calibrations, and REST SDK schemas, go to the official docs page:
            </p>
          </div>
          <div style="display: flex; flex-direction: column; gap: 0.5rem; align-items: flex-start;">
            <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="btn-keynote-primary" style="text-decoration: none; padding: 0.85rem 1.75rem; font-size: 0.92rem; font-weight: 800; white-space: nowrap; display: inline-flex; align-items: center; gap: 0.5rem;">
              <span>GO TO DOCS PAGE ↗</span>
            </a>
            <span style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--c-accent); font-weight: 600;">
              https://floodlock-docs.pages.dev/
            </span>
          </div>
        </div>

      </div>

      <!-- 3. HOW IT WORKS: 4-STEP PIPELINE -->"""

if 'GO TO DOCS PAGE ↗' not in html:
    html = html.replace(exec_briefing_target, exec_briefing_replacement, 1)
    print("6. Added prominent Docs Callout Banner below Executive Briefing.")

# ═══════════════════════════════════════════════════════════════════════════
# 7. ADD DOCS CALLOUT IN DEVELOPER SDK & SOVEREIGN FOOTER BANNER
# ═══════════════════════════════════════════════════════════════════════════
sdk_target = """        <!-- Code Terminal Deck -->
        <div class="code-terminal-deck" style="margin: 1.5rem 0;">"""

sdk_docs_strip = """        <!-- Bold Docs Strip -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.8rem; padding: 0.85rem 1.25rem; margin-bottom: 1rem; border-radius: 12px; background: rgba(180, 83, 9, 0.1); border: 1px solid var(--c-accent);">
          <div style="font-size: 0.9rem; color: var(--c-text-primary);">
            📖 <strong>Need full API references &amp; Python SDK tutorials?</strong> Go to the official documentation page:
          </div>
          <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" style="font-family: var(--font-btn); font-size: 0.82rem; font-weight: 800; color: var(--c-accent); text-decoration: underline; letter-spacing: 0.05em;">
            https://floodlock-docs.pages.dev/ ↗
          </a>
        </div>

        <!-- Code Terminal Deck -->
        <div class="code-terminal-deck" style="margin: 1.5rem 0;">"""

if 'Need full API references &amp; Python SDK tutorials?' not in html:
    html = html.replace(sdk_target, sdk_docs_strip, 1)
    print("7. Added Docs link strip above Code Terminal.")

# Also add to sovereign banner footer
sovereign_target = """          <div style="display: flex; flex-direction: column; gap: 0.6rem; min-width: 240px;">
            <a href="mailto:contact@lanternmechatronics.com" class="btn-keynote-primary" style="justify-content: center; text-decoration: none; padding: 0.65rem 1.2rem; font-size: 0.86rem;">
              <span>Institutional Pilot Briefing →</span>
            </a>"""

sovereign_replacement = """          <div style="display: flex; flex-direction: column; gap: 0.6rem; min-width: 240px;">
            <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="btn-keynote-primary" style="justify-content: center; text-decoration: none; padding: 0.75rem 1.3rem; font-size: 0.88rem; font-weight: 800; background: var(--c-leather); border-color: var(--c-leather-light);">
              <span>📖 Open Documentation Portal ↗</span>
            </a>
            <a href="mailto:contact@lanternmechatronics.com" class="btn-keynote-secondary" style="justify-content: center; text-decoration: none; padding: 0.65rem 1.2rem; font-size: 0.86rem;">
              <span>Institutional Pilot Briefing →</span>
            </a>"""

if 'Open Documentation Portal ↗' not in html:
    html = html.replace(sovereign_target, sovereign_replacement, 1)
    print("8. Added Documentation Portal button in Sovereign Footer Banner.")

# ═══════════════════════════════════════════════════════════════════════════
# 8. ADD PROMINENT DOCS BANNER IN VIEW-API
# ═══════════════════════════════════════════════════════════════════════════
view_api_target = """    <section id="view-api" class="view-section">
      <div class="card-luxury" style="margin-bottom: 2rem;">
        <div style="font-family: var(--font-mono); font-size: 0.75rem; color: #38bdf8; margin-bottom: 0.4rem;">DEVELOPER ARCHITECTURE &amp; APIS</div>
        <h2 style="font-family: var(--font-display); font-size: 2.4rem; margin-bottom: 0.75rem;">MeteoFlood API Platform</h2>
        <p style="color: var(--c-text-muted); font-size: 0.95rem; margin-bottom: 1.5rem;">
          Access ultra-low-latency 14-feature neural predictions, GloFAS river discharge time series, and 150km radius alerts via our edge REST API or official libraries.
        </p>"""

view_api_replacement = """    <section id="view-api" class="view-section">
      <div class="card-luxury" style="margin-bottom: 2rem;">
        <div style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--c-accent); margin-bottom: 0.4rem;">DEVELOPER ARCHITECTURE &amp; APIS</div>
        <h2 style="font-family: var(--font-editorial); font-size: 2.4rem; margin-bottom: 0.75rem;">MeteoFlood API Platform</h2>
        <p style="color: var(--c-text-secondary); font-size: 0.95rem; margin-bottom: 1.5rem;">
          Access ultra-low-latency 14-feature neural predictions, GloFAS river discharge time series, and 150km radius alerts via our edge REST API or official libraries.
        </p>

        <!-- Prominent Docs Callout in API View -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding: 1.2rem 1.6rem; margin-bottom: 1.8rem; border-radius: 14px; background: rgba(180, 83, 9, 0.12); border: 2px solid var(--c-accent);">
          <div>
            <div style="font-family: var(--font-btn); font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--c-accent); font-weight: 800; margin-bottom: 0.2rem;">
              OFFICIAL DOCUMENTATION PORTAL
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: var(--c-text-primary); margin-bottom: 0.25rem;">
              Full OpenAPI Spec, SDK References &amp; Architecture Guides
            </div>
            <div style="font-size: 0.88rem; color: var(--c-text-secondary);">
              For more info and complete endpoint specifications, go to the documentation page:
            </div>
          </div>
          <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="btn-keynote-primary" style="text-decoration: none; padding: 0.75rem 1.4rem; font-size: 0.88rem; font-weight: 800; white-space: nowrap;">
            <span>floodlock-docs.pages.dev ↗</span>
          </a>
        </div>"""

if 'Full OpenAPI Spec, SDK References' not in html:
    html = html.replace(view_api_target, view_api_replacement, 1)
    print("9. Added Docs Callout to #view-api platform view.")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved all documentation links to index.html successfully.")

