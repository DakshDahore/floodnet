``markdown
# 03 — DUAL NEURAL NETWORK ARCHITECTURE & TRAINING SPECIFICATION
**Target Directory:** `/home/daksh/Documents/Projects/floodlock/floodlock_trainer`

---

## 1. EXACT MODEL TOPOLOGIES & PARAMETER ASSERTIONS (`models.py`)

### Model 1: Tier-1 Browser Edge Network (`BrowserEdgeMLP` — Trained FIRST)
- **Role:** Runs inside the user's browser in pure vanilla JavaScript (`inference.js`) at `<0.05 ms` latency (60 FPS slider updates).
- **Inputs (3 Normalized Features $\in [0, 1]$):**
  1. `rain_norm = rain_instant_mm_hr / 200.0`
  2. `eff_tide_norm = (effective_tide_m - 1.0) / 4.5`
  3. `subsidence_norm = subsidence_mm_yr / 40.0`
- **Architecture:**
  - `fc1`: `nn.Linear(3, 16)` $\rightarrow$ Weights: $3 \times 16 = 48$, Biases: $16 \implies 64$ params
  - `relu1`: `nn.ReLU()`
  - `fc2`: `nn.Linear(16, 8)` $\rightarrow$ Weights: $16 \times 8 = 128$, Biases: $8 \implies 136$ params
  - `relu2`: `nn.ReLU()`
  - `fc3`: `nn.Linear(8, 1)` $\rightarrow$ Weights: $8 \times 1 = 8$, Biases: $1 \implies 9$ params
  - Output Activation: `torch.clamp(out, 0.0, 1.0)` (Scaled by $\times 180.0$ for minutes)
- **Total Trainable Parameters:** $64 + 136 + 9 = \mathbf{209}$
- **Mandatory Code Assertion:**
  ```python
  assert sum(p.numel() for p in model_209.parameters() if p.requires_grad) == 209
