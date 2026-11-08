"""
floodlock_trainer/models.py
────────────────────────────────────────────────────────────────────────────
Dual Neural Network Architectures for Project FloodLock:
  - Model 1: BrowserEdgeMLP (Tier 1 Edge Engine, 209 Parameters)
  - Model 2: BackendDeepMLP (Tier 2 Deep Engine, 737 Parameters)
"""

import torch
import torch.nn as nn


class BrowserEdgeMLP(nn.Module):
    """
    Tier 1 Browser Edge Engine: Exactly 209 Parameters.
    Designed for sub-0.05ms forward passes in vanilla JavaScript (inference.js).

    Inputs (3 Normalized Features in [0, 1]):
      1. rain_norm = rain_instant_mm_hr / 200.0
      2. eff_tide_norm = (effective_tide_m - 1.0) / 4.5
      3. subsidence_norm = subsidence_mm_yr / 40.0

    Topology:
      fc1: Linear(3, 16)  -> 3*16 + 16 = 64
      relu1: ReLU()
      fc2: Linear(16, 8)  -> 16*8 + 8 = 136
      relu2: ReLU()
      fc3: Linear(8, 1)   -> 8*1 + 1 = 9
      Total: 64 + 136 + 9 = 209 parameters.

    Output (1): Normalized Inundation ETA in [0, 1] (Scaled by * 180.0 for minutes).
    """
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(3, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class BackendDeepMLP(nn.Module):
    """
    Tier 2 Deep Backend Engine: Exactly 737 Parameters.
    High-capacity neural sentinel running in Python (FastAPI / PyTorch or pure NumPy).

    Inputs (5 Normalized Features in [0, 1]):
      1. rain_norm = rain_instant_mm_hr / 200.0
      2. rain_1hr_norm = rain_1hr_mm_hr / 200.0
      3. pressure_norm = (pressure_hpa - 960.0) / 65.0
      4. eff_tide_norm = (effective_tide_m - 1.0) / 4.5
      5. subsidence_norm = subsidence_mm_yr / 40.0

    Topology:
      fc1: Linear(5, 32)  -> 5*32 + 32 = 192
      relu1: ReLU()
      fc2: Linear(32, 16) -> 32*16 + 16 = 528
      relu2: ReLU()
      fc3: Linear(16, 1)  -> 16*1 + 1 = 17
      Total: 192 + 528 + 17 = 737 parameters.

    Output (1): Normalized Inundation ETA in [0, 1] (Scaled by * 180.0 for minutes).
    """
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(5, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def verify_parameter_counts():
    """
    Strictly asserts exact parameter counts as mandated by specifications:
      - BrowserEdgeMLP == 209
      - BackendDeepMLP == 737
    """
    model_209 = BrowserEdgeMLP()
    model_737 = BackendDeepMLP()

    p_209 = sum(p.numel() for p in model_209.parameters() if p.requires_grad)
    p_737 = sum(p.numel() for p in model_737.parameters() if p.requires_grad)

    assert p_209 == 209, f"FATAL: BrowserEdgeMLP expected 209 parameters, got {p_209}"
    assert p_737 == 737, f"FATAL: BackendDeepMLP expected 737 parameters, got {p_737}"

    return p_209, p_737


if __name__ == "__main__":
    count_209, count_737 = verify_parameter_counts()
    print("=" * 68)
    print(" PROJECT FLOODLOCK // MODEL TOPOLOGY AUDIT")
    print("=" * 68)
    print(f"  [✓] BrowserEdgeMLP: {count_209} parameters (Required: 209)")
    print(f"  [✓] BackendDeepMLP: {count_737} parameters (Required: 737)")
    print("  [✓] Exact topology assertions passed.")
    print("=" * 68)
