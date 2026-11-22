# 🌍 FLOODLOCK GLOBAL PLANETARY HYDROLOGICAL MODEL SPECIFICATION
**Version**: 2.0.0 (Global Planetary Architecture)  
**Target Domain**: Universal Global Flash Flood, Pluvial Inundation & Fluvial Basin Defense  
**Scope**: 100% Scalable to Any Geographic Coordinate on Earth (Inland & Coastal)

---

## 1. Architectural Philosophy: Why Generalization Matters
* **Elimination of Localized Sluice Bias**: Coastal tidal sluice gates are specific to a handful of engineered cities (Mumbai, Rotterdam, London). Inland cities (Delhi, Bengaluru, Paris, Nairobi, Kansas City) experience catastrophic pluvial flash floods without any tidal infrastructure.
* **Planetary Universal Schema**: The model takes general, globally accessible atmospheric, topographic, antecedent hydrological, and geospatial distance features.
* **Conditional Ocean Masking**: Coastal marine surges are conditionally activated only when a coordinate lies within 15 km of sea/ocean; inland basins gracefully mask this input to zero.

---

## 2. Universal 14-Feature Input Vector Definition

| # | Feature Name | Physical Dimension / Range | Time Window | Authoritative Global Data Source |
| :--- | :--- | :--- | :--- | :--- |
| **X1** | **Instant Rain Rate ($R_0$)** | $0 - 250\text{ mm/hr}$ | Real-time | WMO / Open-Meteo High-Res Radar |
| **X2** | **2-Day Cumulative Rain ($R_{48h}$)** | $0 - 500\text{ mm}$ | 48-Hour Rolling Sum | Open-Meteo / ECMWF IFS |
| **X3** | **5-Day Cumulative Rain ($R_{120h}$)** | $0 - 1000\text{ mm}$ | 120-Hour Rolling Sum | Open-Meteo / ECMWF IFS |
| **X4** | **Convective Instability (CAPE)** | $0 - 4500\text{ J/kg}$ | Real-time Hourly | ECMWF IFS / DWD ICON |
| **X5** | **Barometric Pressure Drop ($\Delta P/\Delta t$)** | $-15\text{ to }+5\text{ hPa/hr}$ | 3-Hour Tendency | GFS / ECMWF Global Telemetry |
| **X6** | **Wind Vector Velocity ($\|\vec{V}_{\text{wind}}\|$)** | $0 - 180\text{ km/h}$ | Real-time | ECMWF Global Surface Wind |
| **X7** | **30-Day Precipitation Anomaly (SPI-30)** | $-3.0\text{ to }+3.0\sigma$ | 30-Day Historical | Open-Meteo Historical Archive |
| **X8** | **90-Day Seasonal Rainfall Anomaly (SPI-90)** | $-3.0\text{ to }+3.0\sigma$ | 90-Day Historical | Open-Meteo Historical Archive |
| **X9** | **Root-Zone Soil Saturation (0–100cm)** | $0.0 - 1.0$ (0% to 100%) | Hourly | Copernicus ERA5-Land Reanalysis |
| **X10** | **Hydrologic Soil Group Permeability (HSG)** | Type A (Sand) $\to$ D (Clay) | Static Grid | ISRIC / FAO Global SoilGrids 250m |
| **X11** | **Distance to Nearest Water Body ($D_{\text{water}}$)** | $0 - 50,000\text{ meters}$ | Spatial Vector | HydroRIVERS / OSM Waterways |
| **X12** | **Topographic Wetness Index (TWI) & Slope** | $\ln(\alpha / \tan \beta)$ | Spatial 30m DEM | NASA SRTM 30m Topography |
| **X13** | **Urban Impervious Surface Ratio ($f_{\text{imp}}$)** | $0.0 - 1.0$ (Vegetation $\to$ Asphalt) | Spatial 100m Grid | Copernicus Global Land Cover |
| **X14** | **Conditional Coastal Tide / Surge ($h_{\text{surge}}$)** | $0.0 - 6.0\text{ meters}$ (0 if inland) | Hourly Marine | NOAA CO-OPS / Copernicus Marine |

---

## 3. Multi-Head Predictive Targets

$$\vec{Y} = \begin{bmatrix} h_{\text{depth}}(t+1h), & h_{\text{depth}}(t+3h), & h_{\text{depth}}(t+6h) \\ Q_{\text{velocity}}, & P(\text{Flash Flood}), & \text{Urgency Index} \end{bmatrix}$$

1. **Inundation Water Depth Vector ($h_{\text{depth}}$)**: Predicted street surface water depth in centimeters at +1 hour, +3 hours, and +6 hours lead time.
2. **Surface Runoff Velocity ($Q_{\text{velocity}}$)**: In $m^3/s$ via Manning's overland kinematic wave formulation.
3. **Flash Flood & River Breach Probability ($P$)**: Categorical risk (0.0 to 1.0).
4. **Actionable Evacuation Urgency Index**: Ranked 0.0 (Green / Passable) to 1.0 (Critical / Severe Threat), piped into Google Gemini 1.5 Flash for automated civic advisory generation.

---

## 4. Deep Recurrent Neural Topology

```
Input: Tensor[Batch, 6 Timesteps, 14 Features]
  │
  ▼
Conv1D (Channels: 14 -> 64, Kernel: 1, LeakyReLU)
  │
  ▼
Bidirectional LSTM (Hidden: 128, Layers: 2, Dropout: 0.15)
  │
  ▼
Multi-Head Self-Attention Pooling (Key/Query Dimension: 64)
  │
  ├──────────────────────┬──────────────────────┬──────────────────────┐
  ▼                      ▼                      ▼                      ▼
Depth Head            Runoff Head            Probability Head       Evacuation Head
Linear(256 -> 64)     Linear(256 -> 32)      Linear(256 -> 32)      Linear(256 -> 32)
Linear(64 -> 3)       Linear(32 -> 1)        Linear(32 -> 1)        Linear(32 -> 1)
Output: [h1, h3, h6]  Output: Q [m3/s]       Sigmoid: [0.0 - 1.0]   Sigmoid: [0.0 - 1.0]
```

---

## 5. Planetary Open Data Ingestion Pipeline

All 14 features are retrieved on-demand via zero-cost, high-reliability REST endpoints:
* **Real-time & Historical Weather**: `https://api.open-meteo.com/v1/forecast` & `/v1/archive`
* **Marine Surge**: `https://marine-api.open-meteo.com/v1/marine`
* **Geospatial Elevation**: NASA SRTM 30m Elevation Grid via Open-Elevation / USGS.
* **Nearest River Distance**: HydroRIVERS geometric spatial k-d tree queried in-memory.

