# 02 — HYDRODYNAMIC PHYSICS, WIND VECTORING & UNSEEN CSV SPECIFICATION
**Target Directory:** `/home/daksh/Documents/Projects/floodlock/data` & `floodlock_trainer/generate_datasets.py`

---

## 1. EMPIRICAL HYDROLOGICAL & WIND CONSTANTS
All synthetic data generation and backend harmonizer calculations must obey these exact physical equations for Mumbai's F-South Ward:

1. **Geographic Coordinates & Elevations:**
   - **Hindmata Saucer Basin:** `19.0160° N, 72.8430° E` | Lowest street invert: `+1.80 m MSL` | Saucer retention threshold before curb overtopping: `45.0 mm` (`0.045 m`等效 runoff depth before rapid street pooling).
   - **Love Grove Outfall Sluice Gates (Worli):** `19.0065° N, 72.8165° E` | Outfall Crown Invert: `3.00 m MSL`.
   - **Dadar TT Elevated Viaduct:** `+8.50 m MSL` (Flood-immune evacuation corridor).

2. **Onshore Wind Setup & Orographic Rainfall Amplification:**
   - Onshore azimuth perpendicular to the Worli/Mahim coastline: $\theta_{\text{shore}} = 250.0^\circ$ (West-Southwest monsoon gale vector).
   - Given wind speed $v_w$ ($\text{m/s}$) and wind direction $\theta_w$ ($\text{degrees}$):
     $$v_{\text{onshore}} = \max\left(0.0, \, v_w \cdot \cos\left(\text{radians}(\theta_w - 250.0^\circ)\right)\right)$$
   - Wind-driven coastal surge ($\Delta H_{\text{wind}}$ in meters):
     $$\Delta H_{\text{wind}} = 0.00048 \cdot (v_{\text{onshore}})^2$$
   - Wind-driven convective/orographic rain intensity multiplier:
     $$R_{\text{eff}} = R_{\text{instant}} \cdot (1.0 + 0.006 \cdot v_{\text{onshore}})$$

3. **Inverted Barometer Surge ($\Delta H_{\text{baro}}$):**
   - Standard atmospheric pressure $P_0 = 1013.25\text{ hPa}$. Every $1\text{ hPa}$ drop raises local sea level by $1\text{ cm}$ ($0.01\text{ m}$):
     $$\Delta H_{\text{baro}} = \max\left(0.0, \, (1013.25 - P_{\text{surface}}) \cdot 0.01\right)$$

4. **Effective Coastal Sea Level ($H_{\text{eff}}$):**
   $$H_{\text{eff}} = H_{\text{astro\_tide}} + \Delta H_{\text{baro}} + \Delta H_{\text{wind}}$$

5. **BRIMSTOWAD Gravity Drainage Cap & Sluice Choke ($Q_{\text{drain}}$):**
   - Maximum gravity drainage capacity = $25.0\text{ mm/hr}$.
   - Sluice gates begin choking at $H_{\text{eff}} = 2.60\text{ m MSL}$ and reach **100% Hydraulic Lock ($Q_{\text{drain}} = 0\text{ mm/hr}$)** at $H_{\text{eff}} \ge 3.00\text{ m MSL}$:
     $$\text{Choke\_Ratio} = \operatorname{clamp}\left(\frac{H_{\text{eff}} - 2.60}{3.00 - 2.60}, \, 0.0, \, 1.0\right)$$
     $$Q_{\text{drain}} = 25.0 \cdot (1.0 - \text{Choke\_Ratio})$$

6. **Net Basin Accumulation & InSAR Subsidence Penalty ($\text{ETA}$ in Minutes):**
   - Weighted runoff inflow:
     $$Q_{\text{inflow}} = 0.70 \cdot R_{\text{eff}} + 0.30 \cdot R_{\text{1hr}}$$
   - Net accumulation rate:
     $$\Delta Q = \max(0.0, \, Q_{\text{inflow}} - Q_{\text{drain}})$$
   - InSAR vertical land subsidence ($S \in [0.8, 35.0]\text{ mm/yr}$, Hindmata baseline $14.2\text{ mm/yr}$) reduces effective basin storage capacity by $(1.0 - \frac{S}{110.0})$:
     $$\text{ETA}_{\text{minutes}} = \begin{cases} \operatorname{clamp}\left(\frac{45.0}{\Delta Q} \cdot 60.0 \cdot \left(1.0 - \frac{S}{110.0}\right) + \mathcal{N}(0, 1.2), \, 2.0, \, 180.0\right) & \text{if } \Delta Q > 1.0\text{ mm/hr} \\ 180.0 & \text{if } \Delta Q \le 1.0\text{ mm/hr} \end{cases}$$

---

## 2. DUAL CSV DATASETS (TRAINING VS. UNSEEN GENERALIZATION PROOF)
`floodlock_trainer/generate_datasets.py` must generate two separate CSV files inside `/home/daksh/Documents/Projects/floodlock/data/` with exact header columns:
```csv
rain_instant_mm_hr,rain_1hr_mm_hr,pressure_hpa,tide_astro_m,wind_speed_ms,wind_dir_deg,subsidence_mm_yr,effective_tide_m,choke_pct,eta_minutes
