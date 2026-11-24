#!/usr/bin/env python3
import re
import sys

INDEX_FILE = "floodlock_frontend/index.html"

def main():
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    orig_len = len(content)
    print(f"Original file length: {orig_len} characters")

    # 1. Update switchView function to strictly guard all protected routes
    old_switch_view = """    function switchView(viewId) {
      const session = window.FloodConfig ? window.FloodConfig.getSessionToken() : null;
      if (viewId === 'account' && !session) {
        showFloatingToast('Please sign in to access your Account Dashboard', true);
        viewId = 'auth';
      }"""

    new_switch_view = """    function switchView(viewId) {
      const session = window.FloodConfig ? window.FloodConfig.getSessionToken() : null;
      const protectedViews = ['dashboard', 'api', 'account', 'settings'];
      if (protectedViews.includes(viewId) && !session) {
        const viewLabels = {
          dashboard: 'Tactical Command Radar',
          api: 'Developer API Platform',
          account: 'Account Dashboard',
          settings: 'Application Settings'
        };
        showFloatingToast('Authentication Required: Please sign in to access ' + (viewLabels[viewId] || viewId.toUpperCase()), true);
        viewId = 'auth';
      }"""

    if old_switch_view in content:
        content = content.replace(old_switch_view, new_switch_view, 1)
        print("✓ Successfully updated switchView route guard")
    else:
        print("✗ Could not find old switchView function block")
        sys.exit(1)

    # 2. Update mobileDrawer HTML to segregate Pre-Login and Post-Login links
    old_drawer_links = """    <div style="display: flex; flex-direction: column; gap: 0.35rem; flex: 1;">
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('welcome');">
        <span>🌊</span> <span>Intro Story</span>
      </div>
      <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="mobile-drawer-link" style="text-decoration: none; font-weight: 800; color: var(--c-accent);">
        <span>📖</span> <span>Documentation Portal ↗</span>
      </a>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); openAiModelModal();">
        <span>⚡</span> <span>70B AI Specs &amp; Accuracy (94.2%)</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('dashboard');">
        <span>🛰️</span> <span>Tactical Map &amp; Basins</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('api');">
        <span>⚡</span> <span>API Platform</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); openCommercialInquiryModal();">
        <span>💼</span> <span>Commercial License</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('opensource');">
        <span>📦</span> <span>Open Source</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); scrollToFaq();">
        <span>❓</span> <span>Frequently Asked Questions</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('settings');">
        <span>⚙️</span> <span>Application Settings</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('auth');">
        <span>🔐</span> <span>Sign In / Authentication</span>
      </div>
    </div>"""

    new_drawer_links = """    <!-- Pre-Login Mobile Navigation (Unauthenticated Visitors) -->
    <div id="mobileDrawerPreLogin" style="display: flex; flex-direction: column; gap: 0.35rem; flex: 1;">
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('welcome');">
        <span>🌊</span> <span>Intro Story</span>
      </div>
      <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="mobile-drawer-link" style="text-decoration: none; font-weight: 800; color: var(--c-accent);">
        <span>📖</span> <span>Documentation Portal ↗</span>
      </a>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); openAiModelModal();">
        <span>⚡</span> <span>70B AI Specs &amp; Accuracy</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); openCommercialInquiryModal();">
        <span>💼</span> <span>Commercial License</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('opensource');">
        <span>📦</span> <span>Open Source</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); scrollToFaq();">
        <span>❓</span> <span>Frequently Asked Questions</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('auth');" style="background: var(--c-btn-primary-bg); color: var(--c-btn-primary-text); font-weight: 700; margin-top: 0.75rem; border: 1px solid var(--c-btn-primary-border); justify-content: center;">
        <span>🔐</span> <span>Sign In / Access Gate →</span>
      </div>
    </div>

    <!-- Post-Login Mobile Navigation (Authenticated Operators) -->
    <div id="mobileDrawerPostLogin" style="display: none; flex-direction: column; gap: 0.35rem; flex: 1;">
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('dashboard');">
        <span>🛰️</span> <span>Tactical Command Radar</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('api');">
        <span>⚡</span> <span>API Platform</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('account');">
        <span>👤</span> <span>My Account Dashboard</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('settings');">
        <span>⚙️</span> <span>Application Settings</span>
      </div>
      <a href="https://floodlock-docs.pages.dev/" target="_blank" rel="noopener noreferrer" class="mobile-drawer-link" style="text-decoration: none; font-weight: 800; color: var(--c-accent);">
        <span>📖</span> <span>Documentation Portal ↗</span>
      </a>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); openAiModelModal();">
        <span>⚡</span> <span>70B AI Specs (94.2% Acc)</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); openCommercialInquiryModal();">
        <span>💼</span> <span>Commercial License</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('opensource');">
        <span>📦</span> <span>Open Source</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); switchView('contact');">
        <span>🔬</span> <span>Contribute Ground Truth</span>
      </div>
      <div class="mobile-drawer-link" onclick="closeMobileDrawer(); logoutSession();" style="color: #ef4444; margin-top: 0.75rem; border-top: 1px solid rgba(239, 68, 68, 0.25); padding-top: 0.85rem; font-weight: 600;">
        <span>🚪</span> <span>Sign Out</span>
      </div>
    </div>"""

    if old_drawer_links in content:
        content = content.replace(old_drawer_links, new_drawer_links, 1)
        print("✓ Successfully replaced mobile drawer links with Pre/Post login segregation")
    else:
        print("✗ Could not find old mobile drawer links block")
        sys.exit(1)

    # 3. Update applyLoggedInState and logoutSession to toggle mobile drawer lists
    old_apply_logged_in = """    function applyLoggedInState(user) {
      if (!user) return;
      document.getElementById('dockPreLogin').style.display = 'none';
      document.getElementById('dockPostLogin').style.display = 'flex';"""

    new_apply_logged_in = """    function applyLoggedInState(user) {
      if (!user) return;
      document.getElementById('dockPreLogin').style.display = 'none';
      document.getElementById('dockPostLogin').style.display = 'flex';
      const mPre = document.getElementById('mobileDrawerPreLogin');
      const mPost = document.getElementById('mobileDrawerPostLogin');
      if (mPre) mPre.style.display = 'none';
      if (mPost) mPost.style.display = 'flex';"""

    if old_apply_logged_in in content:
        content = content.replace(old_apply_logged_in, new_apply_logged_in, 1)
        print("✓ Successfully updated applyLoggedInState for mobile drawer")
    else:
        print("✗ Could not find old applyLoggedInState")
        sys.exit(1)

    old_logout_session = """    function logoutSession() {
      window.FloodConfig.clearSession();
      document.getElementById('dockPreLogin').style.display = 'flex';
      document.getElementById('dockPostLogin').style.display = 'none';"""

    new_logout_session = """    function logoutSession() {
      window.FloodConfig.clearSession();
      document.getElementById('dockPreLogin').style.display = 'flex';
      document.getElementById('dockPostLogin').style.display = 'none';
      const mPre = document.getElementById('mobileDrawerPreLogin');
      const mPost = document.getElementById('mobileDrawerPostLogin');
      if (mPre) mPre.style.display = 'flex';
      if (mPost) mPost.style.display = 'none';"""

    if old_logout_session in content:
        content = content.replace(old_logout_session, new_logout_session, 1)
        print("✓ Successfully updated logoutSession for mobile drawer")
    else:
        print("✗ Could not find old logoutSession")
        sys.exit(1)

    # 4. Inject Comprehensive High-Performance Mobile Responsive CSS
    mobile_css = """
    /* ══════════════════════════════════════════════════════════════════
       HIGH-PERFORMANCE SWISS RESPONSIVE & MOBILE VIEWPORT ENGINE
       ══════════════════════════════════════════════════════════════════ */
    html, body {
      overflow-x: hidden !important;
      width: 100% !important;
      max-width: 100vw !important;
      position: relative;
    }

    @media (max-width: 900px) {
      /* Hide desktop vertical water dock on mobile to eliminate bottom obstruction */
      .water-sidebar {
        display: none !important;
      }
      .main-wrapper {
        margin-left: 0 !important;
        width: 100% !important;
        max-width: 100vw !important;
        padding: 1.25rem 1rem 3.5rem !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
      }
      .site-header {
        padding: 0.65rem 1rem !important;
        width: 100% !important;
        box-sizing: border-box !important;
      }
      .header-center {
        display: none !important;
      }
      .header-brand {
        font-size: 1.35rem !important;
      }
      .header-brand-badge {
        display: none !important;
      }
      .btn-docs-header {
        padding: 0.4rem 0.75rem !important;
        font-size: 0.75rem !important;
      }
      .status-badge {
        padding: 0.35rem 0.6rem !important;
      }
      .status-badge span#telemetryStatusText {
        display: none !important;
      }
      .mobile-hamburger-btn {
        display: flex !important;
        min-width: 40px !important;
        min-height: 40px !important;
      }
    }

    @media (max-width: 680px) {
      .hero-cinematic {
        padding: 2.2rem 0.5rem 1.5rem !important;
      }
      .hero-title-giant {
        font-size: clamp(1.75rem, 6.8vw, 2.35rem) !important;
        line-height: 1.15 !important;
        word-break: break-word !important;
        letter-spacing: 0.01em !important;
      }
      .hero-subtitle-lead {
        font-size: 0.92rem !important;
        line-height: 1.55 !important;
        padding: 0 0.5rem !important;
      }
      .hero-cta-group {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 0.75rem !important;
        max-width: 320px !important;
        margin: 0 auto 2rem !important;
        width: 100% !important;
      }
      .hero-cta-group .btn-keynote-primary,
      .hero-cta-group .btn-keynote-secondary {
        width: 100% !important;
        justify-content: center !important;
        text-align: center !important;
      }
      .hero-stat-strip {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 0.65rem !important;
        padding: 0.85rem !important;
        border-radius: 16px !important;
      }
      .hero-stat-num {
        font-size: 1.45rem !important;
      }
      .hero-stat-lbl {
        font-size: 0.65rem !important;
      }
      .story-canvas-container {
        height: 280px !important;
        margin: 1.75rem 0 !important;
        border-radius: 16px !important;
      }
      .tri-pillar-grid {
        grid-template-columns: 1fr !important;
        gap: 1rem !important;
        margin: 1.8rem 0 !important;
      }
      .tri-pillar-card {
        padding: 1.25rem 1rem !important;
        border-radius: 16px !important;
      }
      .pipeline-grid {
        grid-template-columns: 1fr !important;
        gap: 0.85rem !important;
        margin: 1.8rem 0 !important;
      }
      .split-slider-box {
        height: 380px !important;
        margin: 1.5rem 0 !important;
        border-radius: 16px !important;
      }
      .split-layer {
        padding: 1rem 0.75rem !important;
      }
      .split-layer h3 {
        font-size: 1.1rem !important;
      }
      .split-layer p {
        font-size: 0.78rem !important;
        line-height: 1.4 !important;
      }
      .tensor-matrix-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 0.6rem !important;
        margin: 1.5rem 0 !important;
      }
      .tensor-chip {
        padding: 0.75rem 0.65rem !important;
        border-radius: 12px !important;
      }
      .tensor-chip-index {
        font-size: 0.6rem !important;
      }
      .tensor-chip-name {
        font-size: 0.8rem !important;
      }
      .tensor-chip-physics {
        font-size: 0.68rem !important;
      }
      .bento-showcase {
        grid-template-columns: 1fr !important;
        gap: 1rem !important;
        margin: 1.8rem 0 !important;
      }
      .bento-card {
        padding: 1.25rem 1rem !important;
        border-radius: 16px !important;
      }
      .card-luxury {
        padding: 1.25rem 1rem !important;
        border-radius: 16px !important;
      }
      .sovereign-banner {
        padding: 1.4rem 1rem !important;
        border-radius: 16px !important;
        margin: 2rem 0 !important;
      }
      .radar-deck-container {
        height: 340px !important;
        border-radius: 16px !important;
        margin-bottom: 1.25rem !important;
      }
      .modal-dialog {
        padding: 1.25rem 1rem !important;
        width: 95% !important;
        border-radius: 16px !important;
      }
      .cookie-banner {
        bottom: 16px !important;
        width: calc(100% - 24px) !important;
        padding: 1rem !important;
        border-radius: 14px !important;
      }
      .emergency-fab {
        bottom: 16px !important;
        right: 16px !important;
        padding: 0.55rem 0.85rem !important;
        font-size: 0.75rem !important;
      }
      .chapter-heading-giant {
        font-size: clamp(1.4rem, 5.5vw, 1.85rem) !important;
        line-height: 1.2 !important;
        word-break: break-word !important;
      }
      .testbench-stage-flow {
        grid-template-columns: 1fr !important;
        gap: 0.75rem !important;
      }
      /* Auto-stack 2-column inline grids on mobile */
      div[style*="grid-template-columns: 1fr 1fr"],
      div[style*="grid-template-columns: 1fr 1fr;"] {
        grid-template-columns: 1fr !important;
      }
    }
    """

    # We insert this mobile_css right before </style>
    if "</style>" in content:
        content = content.replace("</style>", mobile_css + "\n  </style>", 1)
        print("✓ Successfully injected mobile responsive CSS engine")
    else:
        print("✗ Could not find </style> tag")
        sys.exit(1)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"File updated. New length: {len(content)} characters (delta: {len(content) - orig_len})")

if __name__ == "__main__":
    main()
