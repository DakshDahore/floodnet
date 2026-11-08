/**
 * floodlock_frontend/js/map_engine.js
 * ────────────────────────────────────────────────────────────────────────────
 * Advanced Monochromatic Geospatial Map Engine for Mumbai F-South Ward.
 * Features:
 *   - 100% Free OpenStreetMap Dark/Light tiles (Zero API key watermark).
 *   - Selective Layer Filters (Elevation, Rain Intensity, Active Floods, Timing, GPS Location).
 *   - Smart Conditional Route (Safe bypass appears ONLY during active water logging / flood).
 *   - Real-time GPS User Locator with proximity safety calculator.
 */

class FloodMapEngine {
  constructor() {
    this.map = null;
    this.tileLayer = null;
    this.currentTheme = "dark";

    // Key Precinct Coordinates
    this.HINDMATA = [19.0160, 72.8430];
    this.LOVE_GROVE = [19.0065, 72.8165];
    this.DADAR_TT = [19.0195, 72.8445];
    this.KEM_HOSPITAL = [19.0025, 72.8415];
    this.WORLI_SEAFACE = [19.0105, 72.8120];

    // Layer Groups for Interactive Toggles
    this.layers = {
      elevation: L.layerGroup(),
      rain: L.layerGroup(),
      flood: L.layerGroup(),
      timing: L.layerGroup(),
      routes: L.layerGroup(),
      user: L.layerGroup()
    };

    this.activeLayers = {
      elevation: true,
      rain: true,
      flood: true,
      timing: true
    };

    this.culvertVector = null;
    this.surfaceRoute = null;
    this.elevatedRoute = null;
    this.userLocationMarker = null;
    this.precinctMarkers = [];
    this.floodContours = [];
  }

  init(containerId = "mapCanvas", theme = "dark") {
    this.currentTheme = theme;

    this.map = L.map(containerId, {
      center: [19.0125, 72.8310],
      zoom: 14,
      zoomControl: false,
      attributionControl: false
    });

    L.control.zoom({ position: "topright" }).addTo(this.map);

    this.updateTileLayer(theme);
    this.buildMapLayers();
    this.setupClickHandler();
  }

  updateTileLayer(theme) {
    if (this.tileLayer) {
      this.map.removeLayer(this.tileLayer);
    }

    // OpenStreetMap standard tiles with CSS monochromatic styling
    // ZERO API KEY REQUIRED - Never watermarks or blocks
    const tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

    this.tileLayer = L.tileLayer(tileUrl, {
      maxZoom: 19,
      subdomains: ["a", "b", "c"],
      className: theme === "light" ? "map-tiles-light" : "map-tiles-dark"
    }).addTo(this.map);
  }

  buildMapLayers() {
    // 1. ELEVATION LAYER (+1.8m, +3.0m, +4.5m, +8.5m topographic references)
    const elevNodes = [
      { pos: this.HINDMATA, label: "+1.8m MSL", name: "Hindmata Basin (Depression)" },
      { pos: this.LOVE_GROVE, label: "+3.0m MSL", name: "Love Grove Sluice Invert" },
      { pos: this.KEM_HOSPITAL, label: "+4.5m MSL", name: "KEM Hospital Plateau" },
      { pos: this.DADAR_TT, label: "+8.5m MSL", name: "Dadar TT Elevated Viaduct" }
    ];

    elevNodes.forEach(n => {
      const icon = L.divIcon({
        className: "elevation-badge-icon",
        html: `<div class="elev-pill">${n.label}</div>`,
        iconSize: [60, 20],
        iconAnchor: [30, 10]
      });
      L.marker(n.pos, { icon }).bindTooltip(n.name).addTo(this.layers.elevation);
    });

    // 2. ACTIVE FLOOD CONTOURS (Concentric risk rings)
    const zones = [
      { radius: 180, color: "#ef4444", fillOpacity: 0.28, label: "Zone 1: Severe Inundation (<2.0m MSL)" },
      { radius: 360, color: "#f59e0b", fillOpacity: 0.18, label: "Zone 2: Surcharge Ponding (<2.5m MSL)" },
      { radius: 600, color: "#06b6d4", fillOpacity: 0.08, label: "Zone 3: Runoff Buffer Zone (<3.2m MSL)" }
    ];

    zones.forEach(z => {
      const circle = L.circle(this.HINDMATA, {
        radius: z.radius,
        color: z.color,
        weight: 1.5,
        dashArray: "4, 6",
        fillColor: z.color,
        fillOpacity: z.fillOpacity
      }).addTo(this.layers.flood);
      this.floodContours.push(circle);
    });

    // 3. RAIN RADAR INTENSITY LAYER
    this.rainRadarCircle = L.circle(this.HINDMATA, {
      radius: 950,
      color: "rgba(56, 189, 248, 0.4)",
      weight: 1.5,
      dashArray: "6, 6",
      fillColor: "rgba(56, 189, 248, 0.12)",
      fillOpacity: 0.15
    }).addTo(this.layers.rain);

    // 4. TIMING & WATER DEPTH TAGS
    this.timingMarker = L.marker([19.0140, 72.8420], {
      icon: L.divIcon({
        className: "timing-badge-icon",
        html: `<div class="timing-pill" id="mapTimingPill">DEPTH: 0.0 cm // ETA: >180m</div>`,
        iconSize: [140, 24],
        iconAnchor: [70, 12]
      })
    }).addTo(this.layers.timing);

    // 5. ROUTING & CULVERT LAYER
    // A. Love Grove Sluice Culvert Vector (Hindmata -> Worli)
    const culvertPath = [
      this.HINDMATA,
      [19.0135, 72.8330],
      [19.0100, 72.8240],
      this.LOVE_GROVE
    ];
    this.culvertVector = L.polyline(culvertPath, {
      color: "#10b981",
      weight: 4.5,
      opacity: 0.9,
      dashArray: "8, 6"
    }).addTo(this.layers.routes);

    // B. Surface Dr. B.A. Road
    const surfacePath = [
      this.DADAR_TT,
      this.HINDMATA,
      [19.0080, 72.8422],
      this.KEM_HOSPITAL
    ];
    this.surfaceRoute = L.polyline(surfacePath, {
      color: "#3b82f6",
      weight: 4.0,
      opacity: 0.85
    }).addTo(this.layers.routes);

    // C. Dadar TT Elevated Viaduct (+8.5m MSL)
    // IMPORTANT: Initially HIDDEN (opacity 0) because normal conditions require no diversion!
    const elevatedPath = [
      [19.0230, 72.8455],
      this.DADAR_TT,
      [19.0160, 72.8445],
      [19.0090, 72.8435],
      this.KEM_HOSPITAL
    ];
    this.elevatedRoute = L.polyline(elevatedPath, {
      color: "#06b6d4",
      weight: 5.5,
      opacity: 0.0 // Hidden in normal conditions
    }).addTo(this.layers.routes);

    // Add Precinct Markers
    this.addPrecinctMarker(this.HINDMATA, "Hindmata Saucer Basin", "+1.8m MSL", "#ef4444");
    this.addPrecinctMarker(this.LOVE_GROVE, "Love Grove Sluice Outfall", "+3.0m MSL Invert", "#10b981");
    this.addPrecinctMarker(this.DADAR_TT, "Dadar TT Viaduct (+8.5m MSL)", "Flood-Immune Bypass", "#06b6d4");
    this.addPrecinctMarker(this.KEM_HOSPITAL, "KEM Hospital Trauma Center", "+4.5m MSL Emergency", "#a855f7");

    // Add all initial layer groups to map
    Object.values(this.layers).forEach(lg => lg.addTo(this.map));
  }

  addPrecinctMarker(latlng, title, elevation, color) {
    const icon = L.divIcon({
      className: "custom-map-pin",
      html: `<div style="background:${color}; width:12px; height:12px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 10px ${color};"></div>`,
      iconSize: [12, 12],
      iconAnchor: [6, 6]
    });

    const marker = L.marker(latlng, { icon }).addTo(this.layers.routes);
    marker.bindTooltip(`<strong>${title}</strong><br><span style="font-family:monospace; font-size:11px;">Elevation: ${elevation}</span>`, {
      className: "tactical-tooltip",
      direction: "top"
    });
    this.precinctMarkers.push(marker);
  }

  /**
   * Toggles individual layers on/off via frontend filter buttons.
   */
  setLayerVisibility(name, visible) {
    if (!this.layers[name]) return;
    this.activeLayers[name] = visible;
    if (visible) {
      this.map.addLayer(this.layers[name]);
    } else {
      this.map.removeLayer(this.layers[name]);
    }
  }

  /**
   * Updates map elements dynamically in real-time based on physics and routing.
   */
  updateDynamicVectors(telemetry, routing) {
    if (!this.culvertVector || !this.surfaceRoute) return;

    const effTide = telemetry.effectiveTide;
    const chokePct = telemetry.chokePct;
    const waterDepth = telemetry.waterDepthM;
    const isFlood = waterDepth >= 0.15 || routing.status.includes("REROUTE");

    // 1. Sluice Culvert Vector (Worli Outfall)
    let culvertColor = "#10b981";
    if (effTide >= 3.0 || chokePct >= 95.0) {
      culvertColor = "#ef4444"; // Total Hydraulic Lock
    } else if (effTide >= 2.6 || chokePct >= 35.0) {
      culvertColor = "#f59e0b"; // Sluice Surcharge Choking
    }
    this.culvertVector.setStyle({ color: culvertColor });

    // 2. CONDITIONAL SAFE ROUTE (Crucial user requirement):
    // Only show elevated bypass when active flood / clogging occurs!
    if (isFlood) {
      // Surface is severed/impassable
      this.surfaceRoute.setStyle({
        color: "#ef4444",
        dashArray: "6, 8",
        weight: 3.5,
        opacity: 0.85
      });
      // Activate glowing Cyan elevated viaduct route!
      this.elevatedRoute.setStyle({
        opacity: 0.95,
        weight: 6.0,
        color: "#06b6d4"
      });
    } else {
      // Normal nominal conditions: Surface is clear, NO diversion needed
      this.surfaceRoute.setStyle({
        color: "#3b82f6",
        dashArray: null,
        weight: 4.0,
        opacity: 0.85
      });
      // Hide elevated route completely so citizen map is clean!
      this.elevatedRoute.setStyle({
        opacity: 0.0
      });
    }

    // 3. Concentric Exposure Contours opacity
    const baseOpacity = isFlood ? Math.min(0.65, 0.20 + (waterDepth * 0.35)) : 0.08;
    this.floodContours.forEach((c, idx) => {
      c.setStyle({ fillOpacity: baseOpacity / (idx + 1) });
    });

    // 4. Update Rain Radar visual intensity
    if (this.rainRadarCircle) {
      const rain = telemetry.rEff || 0;
      const rainOpacity = Math.min(0.55, 0.08 + (rain / 200.0) * 0.45);
      this.rainRadarCircle.setStyle({
        fillOpacity: rainOpacity,
        color: rain > 50 ? "#ef4444" : rain > 20 ? "#f59e0b" : "#38bdf8"
      });
    }

    // 5. Update Timing & Depth badge
    const timingPill = document.getElementById("mapTimingPill");
    if (timingPill) {
      const depthCm = Math.round(waterDepth * 100);
      const etaMin = telemetry.etaPhysics;
      timingPill.textContent = `DEPTH: ${depthCm} cm // ETA: ${etaMin > 120 ? '>120m' : etaMin.toFixed(0) + 'm'}`;
      timingPill.style.color = isFlood ? "#ef4444" : "#10b981";
      timingPill.style.borderColor = isFlood ? "#ef4444" : "var(--border)";
    }
  }

  /**
   * GPS User Locator (Phone / Browser)
   */
  locateUser(callback) {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser/device.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        const accuracy = Math.round(pos.coords.accuracy);

        // Distance to Hindmata hazard basin
        const distM = Math.round(this.map.distance([lat, lng], this.HINDMATA));
        const isHazard = distM < 700;

        if (this.userLocationMarker) {
          this.layers.user.removeLayer(this.userLocationMarker);
        }

        const icon = L.divIcon({
          className: "user-gps-marker",
          html: `<div class="user-pulse-dot" style="background:${isHazard ? '#ef4444' : '#06b6d4'}; box-shadow:0 0 16px ${isHazard ? '#ef4444' : '#06b6d4'};"></div>`,
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        });

        this.userLocationMarker = L.marker([lat, lng], { icon })
          .bindPopup(`
            <div style="font-family:'Inter',sans-serif; padding:4px;">
              <strong style="color:${isHazard ? '#ef4444' : '#06b6d4'};">📍 YOUR CURRENT LOCATION</strong><br>
              <div style="font-size:11px; margin-top:4px; font-family:'JetBrains Mono',monospace;">
                GPS Accuracy: ±${accuracy}m<br>
                Distance to Hindmata Basin: ${distM} meters<br>
                Status: <strong style="color:${isHazard ? '#ef4444' : '#10b981'};">${isHazard ? '⚠️ IN FLOOD ADVISORY ZONE' : '✓ ELEVATED & SAFE'}</strong>
              </div>
            </div>
          `)
          .addTo(this.layers.user);

        this.map.flyTo([lat, lng], 15, { duration: 1.2 });
        this.userLocationMarker.openPopup();

        if (callback) callback({ lat, lng, distM, isHazard, accuracy });
      },
      (err) => {
        console.warn("GPS location denied or error:", err);
        // Default pan to Hindmata if denied
        this.map.flyTo(this.HINDMATA, 15, { duration: 1.0 });
        if (callback) callback(null);
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  }

  setupClickHandler() {
    this.map.on("click", (e) => {
      const lat = e.latlng.lat.toFixed(4);
      const lng = e.latlng.lng.toFixed(4);
      const distHindmata = e.latlng.distanceTo(L.latLng(this.HINDMATA[0], this.HINDMATA[1]));
      const estElevation = (1.80 + Math.min(6.5, (distHindmata / 600.0) * 2.2)).toFixed(2);

      const popupContent = `
        <div style="font-family:'Inter',sans-serif; min-width:180px; padding:4px;">
          <div style="font-size:10px; font-weight:700; color:#06b6d4; text-transform:uppercase; letter-spacing:0.5px;">Spatial Inspector</div>
          <div style="font-size:12px; font-weight:600; margin:4px 0;">Precinct Point</div>
          <div style="font-family:'JetBrains Mono',monospace; font-size:11px; color:#cbd5e1; line-height:1.6;">
            LAT: ${lat}° N<br>
            LON: ${lng}° E<br>
            ELEVATION: +${estElevation}m MSL<br>
            DRAINAGE BASIN: F-South Ward
          </div>
        </div>
      `;

      L.popup({ className: "tactical-popup" })
        .setLatLng(e.latlng)
        .setContent(popupContent)
        .openOn(this.map);
    });
  }
}

window.FloodMap = new FloodMapEngine();
