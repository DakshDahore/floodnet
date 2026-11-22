# scripts/build_frontend_modular.py
import os

part1 = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FloodLock — Planetary Disaster Intelligence & Compound Flood Physics</title>
  <meta name="description" content="Commercial planetary compound flood forecasting, antecedent soil saturation modeling, and tidal backflow defense engineered for global urban coastal basins.">

  <!-- Safe Luxury Commercial Typography (Google Fonts) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

  <!-- MapLibre GL for High-Speed Vector Maps -->
  <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
  <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>

  <!-- EmailJS Official Browser SDK -->
  <script src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>

  <!-- Chart.js for High-Precision 90-Day Hydrological Hydrographs -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

  <style>
    :root {
      /* Savile Row Coat & Fluid Leather Palette */
      --c-obsidian: #120D09;
      --c-umber: #2A1F17;
      --c-cognac: #92542B;
      --c-cognac-hover: #b86b38;
      --c-sage: #788279;
      --c-beige: #D6C5B3;
      --c-linen: #F8F5EE;
      --c-water: #06b6d4;
      --c-water-glow: rgba(6, 182, 212, 0.4);
      --c-alert: #ef4444;
      --c-watch: #f59e0b;
      --c-nominal: #10b981;
      
      --c-bg: #100C08;
      --c-card-bg: rgba(28, 20, 15, 0.88);
      --c-card-border: rgba(214, 197, 179, 0.18);
      --c-text-muted: #B5A89B;

      --font-display: 'Instrument Serif', Georgia, serif;
      --font-sans: 'Plus Jakarta Sans', -apple-system, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    [data-theme="light"] {
      --c-bg: #F4EFEB;
      --c-card-bg: rgba(255, 255, 255, 0.92);
      --c-card-border: rgba(146, 84, 43, 0.25);
      --c-linen: #1C140E;
      --c-text-muted: #6B5E55;
      --c-obsidian: #EADFD7;
      --c-umber: #DBCDC2;
    }

    [data-theme="cyber"] {
      --c-bg: #050B14;
      --c-card-bg: rgba(10, 25, 47, 0.88);
      --c-card-border: rgba(6, 182, 212, 0.28);
      --c-linen: #E2F1F8;
      --c-text-muted: #8AA4B8;
      --c-cognac: #0ea5e9;
      --c-cognac-hover: #38bdf8;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--c-bg);
      color: var(--c-linen);
      font-family: var(--font-sans);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden;
      transition: background-color 0.3s ease, color 0.3s ease;
    }

    /* ══════════════════════════════════════════════════════════════════
       TOP HEADER
       ══════════════════════════════════════════════════════════════════ */
    header {
      position: sticky;
      top: 0;
      z-index: 900;
      backdrop-filter: blur(28px);
      background: rgba(16, 12, 8, 0.88);
      border-bottom: 1px solid var(--c-card-border);
      padding: 1rem 2.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .brand {
      font-family: var(--font-display);
      font-size: 2.2rem;
      color: var(--c-linen);
      letter-spacing: -0.02em;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .brand span { color: var(--c-cognac); font-style: italic; }
    .header-actions { display: flex; align-items: center; gap: 0.85rem; }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.6rem;
      background: rgba(146, 84, 43, 0.15);
      border: 1px solid rgba(146, 84, 43, 0.4);
      color: var(--c-beige);
      padding: 0.4rem 1rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }
    .status-dot {
      width: 7px;
      height: 7px;
      background-color: var(--c-nominal);
      border-radius: 50%;
      box-shadow: 0 0 10px var(--c-nominal);
      animation: pulseGlow 2s infinite;
    }
    @keyframes pulseGlow { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.85); } }

    /* ══════════════════════════════════════════════════════════════════
       WATERY FLUID SIDEBAR (DYNAMIC DOCK)
       ══════════════════════════════════════════════════════════════════ */
    .water-sidebar {
      position: fixed;
      left: 1.5rem;
      top: 50%;
      transform: translateY(-50%);
      z-index: 1000;
      background: rgba(22, 16, 11, 0.75);
      backdrop-filter: blur(32px) saturate(180%);
      border: 1px solid rgba(214, 197, 179, 0.25);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15);
      border-radius: 36px;
      padding: 0.75rem 0.55rem;
      width: 66px;
      transition: width 0.35s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s ease;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }
    .water-sidebar:hover, .water-sidebar.proximity-expanded {
      width: 220px;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.7), 0 0 25px rgba(6, 182, 212, 0.25);
    }
    .water-dock-item {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 0.75rem 0.85rem;
      border-radius: 24px;
      color: var(--c-text-muted);
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 500;
      white-space: nowrap;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.22s ease;
      position: relative;
    }
    .water-dock-item:hover {
      background: rgba(214, 197, 179, 0.12);
      color: var(--c-linen);
      transform: translateX(3px);
    }
    .water-dock-item.active {
      background: linear-gradient(135deg, rgba(146, 84, 43, 0.4), rgba(6, 182, 212, 0.25));
      border: 1px solid rgba(6, 182, 212, 0.5);
      color: var(--c-linen);
      font-weight: 700;
      box-shadow: 0 4px 15px rgba(6, 182, 212, 0.2);
    }
    .water-dock-item.active .dock-icon {
      color: #38bdf8;
      filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.8));
    }
    .dock-icon {
      font-size: 1.25rem;
      display: flex;
      align-items: center;
      justify-content: center;
      min-width: 28px;
    }
    .dock-label {
      opacity: 0;
      transform: translateX(-10px);
      transition: opacity 0.25s ease, transform 0.25s ease;
      font-family: var(--font-sans);
    }
    .water-sidebar:hover .dock-label, .water-sidebar.proximity-expanded .dock-label {
      opacity: 1;
      transform: translateX(0);
    }

    /* ══════════════════════════════════════════════════════════════════
       MAIN WRAPPER & SECTIONS
       ══════════════════════════════════════════════════════════════════ */
    .main-wrapper {
      margin-left: 90px;
      min-height: calc(100vh - 80px);
      padding: 2rem 2.5rem;
      max-width: 1350px;
      transition: margin-left 0.3s;
    }
    @media (max-width: 900px) {
      .water-sidebar {
        left: 0; top: auto; bottom: 0; transform: none;
        width: 100% !important; height: 64px; border-radius: 20px 20px 0 0;
        flex-direction: row; justify-content: space-around; padding: 0.5rem;
      }
      .dock-label { display: none !important; }
      .main-wrapper { margin-left: 0; padding-bottom: 90px; }
    }
    .view-section {
      display: none; opacity: 0; transform: translateY(14px);
      transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .view-section.active { display: block; opacity: 1; transform: translateY(0); }

    /* Buttons & Cards */
    .btn-magnetic {
      background: linear-gradient(135deg, var(--c-cognac), #6f3b19);
      color: var(--c-linen);
      border: 1px solid rgba(214, 197, 179, 0.4);
      padding: 0.95rem 2.2rem;
      font-size: 1rem;
      font-weight: 600;
      border-radius: 999px;
      cursor: pointer;
      box-shadow: 0 12px 28px -6px rgba(146, 84, 43, 0.45);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      display: inline-flex;
      align-items: center;
      gap: 0.65rem;
      text-decoration: none;
    }
    .btn-magnetic:hover {
      transform: translateY(-2px);
      box-shadow: 0 16px 36px -6px rgba(146, 84, 43, 0.7);
      border-color: var(--c-beige);
      background: linear-gradient(135deg, var(--c-cognac-hover), var(--c-cognac));
    }
    .btn-water {
      background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(14, 165, 233, 0.4));
      border: 1px solid rgba(6, 182, 212, 0.5);
      color: #E2F1F8;
      padding: 0.8rem 1.6rem;
      border-radius: 999px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.25s;
    }
    .btn-water:hover {
      background: linear-gradient(135deg, rgba(6, 182, 212, 0.35), rgba(14, 165, 233, 0.6));
      box-shadow: 0 0 20px rgba(6, 182, 212, 0.4);
      transform: translateY(-2px);
    }
    .card-luxury {
      background: var(--c-card-bg);
      border: 1px solid var(--c-card-border);
      border-radius: 20px;
      padding: 2rem;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4);
      backdrop-filter: blur(20px);
      transition: border-color 0.25s, transform 0.25s;
    }

    /* ══════════════════════════════════════════════════════════════════
       VIEW 1: SCROLL CANVAS & STORYTELLING
       ══════════════════════════════════════════════════════════════════ */
    .story-hero-header { text-align: center; padding: 3rem 1rem 1.5rem; max-width: 950px; margin: 0 auto; }
    .story-hero-header h1 {
      font-family: var(--font-display);
      font-size: 5rem;
      line-height: 1.02;
      letter-spacing: -0.02em;
      margin-bottom: 1.25rem;
      background: linear-gradient(180deg, #FFFFFF 20%, #D6C5B3 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .story-hero-header h1 em { font-style: italic; color: var(--c-cognac); -webkit-text-fill-color: var(--c-cognac); }
    .story-canvas-container {
      position: relative; width: 100%; height: 600px; border-radius: 28px;
      overflow: hidden; border: 1px solid var(--c-card-border);
      box-shadow: 0 30px 80px rgba(0, 0, 0, 0.7); margin: 2.5rem 0; background: #090e17;
    }
    #storyCanvas { width: 100%; height: 100%; display: block; cursor: crosshair; }
    .story-hud-overlay {
      position: absolute; bottom: 1.5rem; left: 1.5rem; right: 1.5rem;
      display: flex; justify-content: space-between; align-items: flex-end; pointer-events: none;
    }
    .story-hud-box {
      background: rgba(14, 10, 7, 0.85); backdrop-filter: blur(20px);
      border: 1px solid rgba(214, 197, 179, 0.25); padding: 1.1rem 1.5rem;
      border-radius: 16px; max-width: 520px; pointer-events: auto;
    }
    .story-hud-tag {
      font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase;
      letter-spacing: 0.12em; color: #38bdf8; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 0.4rem;
    }
    .story-hud-title { font-family: var(--font-display); font-size: 1.6rem; color: var(--c-linen); margin-bottom: 0.4rem; }
    .story-hud-desc { font-size: 0.92rem; color: var(--c-text-muted); line-height: 1.5; }
    .story-timeline-scrubber {
      background: rgba(14, 10, 7, 0.85); backdrop-filter: blur(20px);
      border: 1px solid rgba(214, 197, 179, 0.25); padding: 0.8rem 1.2rem;
      border-radius: 999px; display: flex; align-items: center; gap: 0.8rem; pointer-events: auto;
    }
    .scene-block { margin: 4.5rem 0; display: grid; grid-template-columns: 1fr 1fr; gap: 2.5rem; align-items: center; }
    @media (max-width: 900px) { .scene-block { grid-template-columns: 1fr; } }
    .math-descrambler-box {
      font-family: var(--font-mono); background: rgba(10, 15, 24, 0.92);
      border: 1px solid rgba(6, 182, 212, 0.4); border-radius: 20px; padding: 2.2rem;
      min-height: 220px; display: flex; flex-direction: column; justify-content: center;
      position: relative; box-shadow: 0 0 30px rgba(6, 182, 212, 0.15);
    }
    .math-scramble-text { font-size: 1.15rem; color: #38bdf8; letter-spacing: 0.04em; word-break: break-word; line-height: 1.8; }
    .sources-search-bar {
      display: flex; align-items: center; background: rgba(25, 18, 13, 0.9);
      border: 1px solid rgba(214, 197, 179, 0.35); border-radius: 999px;
      padding: 0.75rem 1.5rem; margin: 1.5rem 0; gap: 1rem;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4); transition: all 0.25s;
    }
    .sources-search-bar:focus-within { border-color: #38bdf8; box-shadow: 0 0 25px rgba(56, 189, 248, 0.35); }
    .sources-search-bar input { flex: 1; background: transparent; border: none; outline: none; color: var(--c-linen); font-size: 1.05rem; }
    .sources-chips { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 1rem; }
    .source-chip {
      background: rgba(214, 197, 179, 0.1); border: 1px solid rgba(214, 197, 179, 0.2);
      border-radius: 999px; padding: 0.35rem 0.9rem; font-size: 0.8rem; font-family: var(--font-mono);
      color: var(--c-beige); cursor: pointer; transition: all 0.2s;
    }
    .source-chip:hover { background: rgba(6, 182, 212, 0.2); border-color: #38bdf8; color: var(--c-linen); }
    .token-stream-terminal {
      background: #050810; border: 1px solid rgba(6, 182, 212, 0.35);
      border-radius: 18px; padding: 1.5rem; font-family: var(--font-mono);
      font-size: 0.9rem; color: #a5f3fc; min-height: 180px; box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.8);
    }
    .token-cursor { display: inline-block; width: 8px; height: 15px; background: #38bdf8; margin-left: 4px; animation: blink 0.8s infinite; }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

    /* Instagram DMs & Shredder */
    .insta-dm-deck {
      background: rgba(20, 14, 10, 0.92); border: 1px solid var(--c-card-border);
      border-radius: 24px; overflow: hidden; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    }
    .insta-dm-header {
      padding: 1rem 1.5rem; background: rgba(30, 22, 16, 0.95);
      border-bottom: 1px solid var(--c-card-border); display: flex; justify-content: space-between; align-items: center;
    }
    .insta-unread-badge {
      background: #ef4444; color: #fff; font-size: 0.75rem; font-weight: 700;
      padding: 0.2rem 0.6rem; border-radius: 999px; box-shadow: 0 0 10px #ef4444; animation: pulse 1.5s infinite;
    }
    .insta-dm-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; max-height: 280px; overflow-y: auto; }
    .dm-bubble { background: rgba(214, 197, 179, 0.08); border: 1px solid rgba(214, 197, 179, 0.15); border-radius: 16px; padding: 0.85rem 1.1rem; font-size: 0.88rem; }
    .dm-bubble strong { color: #38bdf8; display: block; font-size: 0.78rem; margin-bottom: 0.25rem; }
    .dm-input-area { padding: 1rem 1.25rem; border-top: 1px solid var(--c-card-border); display: flex; gap: 0.75rem; align-items: center; position: relative; }
    .dm-input-area input { flex: 1; background: rgba(10, 7, 5, 0.8); border: 1px solid rgba(214, 197, 179, 0.25); border-radius: 999px; padding: 0.6rem 1.2rem; color: var(--c-linen); outline: none; }
    .trash-bin-visual { font-size: 2.2rem; cursor: pointer; transition: transform 0.2s; }
    .trash-bin-visual:hover { transform: scale(1.15) rotate(5deg); }
    .paper-crumple-ball {
      position: absolute; width: 18px; height: 18px; background: #f8fafc;
      border-radius: 50%; box-shadow: 0 2px 6px rgba(0,0,0,0.4); pointer-events: none;
      animation: tossInTrash 0.75s forwards cubic-bezier(0.25, 1, 0.5, 1);
    }
    @keyframes tossInTrash {
      0% { opacity: 1; transform: translate(0, 0) scale(1) rotate(0deg); }
      50% { transform: translate(60px, -40px) scale(0.6) rotate(180deg); }
      100% { opacity: 0; transform: translate(110px, 15px) scale(0.2) rotate(360deg); }
    }
    .founder-code-terminal {
      background: #090d16; border: 1px solid rgba(16, 185, 129, 0.4);
      border-radius: 20px; padding: 2rem; font-family: var(--font-mono);
      font-size: 0.9rem; color: #34d399; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6), inset 0 0 30px rgba(16, 185, 129, 0.08);
      line-height: 1.7;
    }

    /* Radar Map & Radius */
    .radar-deck-container { position: relative; width: 100%; height: 520px; border-radius: 24px; overflow: hidden; border: 1px solid var(--c-card-border); margin-bottom: 2rem; }
    #map { width: 100%; height: 100%; }
    .radar-blip { width: 16px; height: 16px; border-radius: 50%; position: relative; cursor: pointer; box-shadow: 0 0 10px currentColor; }
    .radar-blip::after {
      content: ''; position: absolute; top: -6px; left: -6px; right: -6px; bottom: -6px;
      border-radius: 50%; border: 2px solid currentColor; opacity: 0.8; animation: radarPulse 1.8s ease-out infinite;
    }
    @keyframes radarPulse { 0% { transform: scale(0.6); opacity: 1; } 100% { transform: scale(2.4); opacity: 0; } }
    .blip-critical { color: #ef4444; background: #ef4444; }
    .blip-watch { color: #f59e0b; background: #f59e0b; }
    .blip-nominal { color: #10b981; background: #10b981; }
    .radius-selector-bar { display: flex; gap: 0.5rem; margin: 1.25rem 0; }
    .radius-pill {
      background: rgba(214, 197, 179, 0.1); border: 1px solid rgba(214, 197, 179, 0.25);
      padding: 0.45rem 1rem; border-radius: 999px; color: var(--c-beige);
      font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.2s;
    }
    .radius-pill.active {
      background: var(--c-cognac); border-color: var(--c-cognac-hover);
      color: var(--c-linen); box-shadow: 0 0 12px rgba(146, 84, 43, 0.5);
    }

    /* Modals & Code Boxes */
    .modal-backdrop {
      position: fixed; inset: 0; z-index: 2000; background: rgba(10, 7, 5, 0.85);
      backdrop-filter: blur(24px); display: none; align-items: center; justify-content: center; padding: 1.5rem;
    }
    .modal-backdrop.open { display: flex; }
    .modal-dialog {
      background: rgba(26, 19, 14, 0.95); border: 1px solid rgba(214, 197, 179, 0.3);
      border-radius: 24px; width: 100%; max-width: 640px; max-height: 90vh;
      overflow-y: auto; padding: 2.2rem; box-shadow: 0 25px 70px rgba(0, 0, 0, 0.8); position: relative;
    }
    .modal-close-btn {
      position: absolute; top: 1.5rem; right: 1.5rem; background: rgba(214, 197, 179, 0.1);
      border: 1px solid rgba(214, 197, 179, 0.2); color: var(--c-linen);
      width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer;
    }
    .code-box {
      background: #080c14; border: 1px solid rgba(214, 197, 179, 0.15);
      border-radius: 14px; padding: 1.25rem; font-family: var(--font-mono);
      font-size: 0.85rem; color: #93c5fd; overflow-x: auto; position: relative; margin: 1rem 0;
    }
    .copy-btn {
      position: absolute; top: 0.75rem; right: 0.75rem; background: rgba(214, 197, 179, 0.15);
      border: 1px solid rgba(214, 197, 179, 0.25); color: var(--c-linen);
      padding: 0.3rem 0.65rem; border-radius: 6px; font-size: 0.75rem; cursor: pointer;
    }
  </style>
</head>
<body>
"""

with open("/home/daksh/Projects/floodlock/floodlock_frontend/index.html", "w", encoding="utf-8") as f:
    f.write(part1)
print("Part 1 written")
