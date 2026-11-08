"""
floodlock_trainer/train_models.py
────────────────────────────────────────────────────────────────────────────
Unified Training Pipeline for Project FloodLock Dual Neural Networks:
  - Model 1: BrowserEdgeMLP (Tier 1 Edge, 209 Parameters — Trained FIRST)
  - Model 2: BackendDeepMLP (Tier 2 Deep, 737 Parameters — Trained SECOND)

Evaluates and logs epoch losses against:
  - data/train_telemetry.csv (4,000 training distribution samples)
  - data/holdout_unseen_telemetry.csv (1,000 out-of-distribution extremes)

Exports real serialized weights to:
  - floodlock_trainer/exports/weights_browser.json
  - floodlock_trainer/exports/weights_backend.json
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import csv
import json
import time
import shutil
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from models import BrowserEdgeMLP, BackendDeepMLP, verify_parameter_counts
from generate_datasets import generate_all, TRAIN_CSV, HOLDOUT_CSV

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRAINER_DIR = os.path.dirname(os.path.abspath(__file__))
CHECKPOINT_DIR = os.path.join(TRAINER_DIR, "checkpoints")
EXPORT_DIR = os.path.join(TRAINER_DIR, "exports")
FRONTEND_DATA_DIR = os.path.join(BASE_DIR, "floodlock_frontend", "data")
BACKEND_LOCAL_DATA_DIR = os.path.join(BASE_DIR, "floodlock_backend_local", "data")
BACKEND_CLOUD_DATA_DIR = os.path.join(BASE_DIR, "floodlock_backend_cloud", "data")

os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_telemetry_csv(filepath: str):
    """
    Loads telemetry CSV and converts to float32 tensors for both models.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    rain_inst = np.array([float(r["rain_instant_mm_hr"]) for r in rows], dtype=np.float32)
    rain_1hr = np.array([float(r["rain_1hr_mm_hr"]) for r in rows], dtype=np.float32)
    pressure = np.array([float(r["pressure_hpa"]) for r in rows], dtype=np.float32)
    eff_tide = np.array([float(r["effective_tide_m"]) for r in rows], dtype=np.float32)
    subsidence = np.array([float(r["subsidence_mm_yr"]) for r in rows], dtype=np.float32)
    eta = np.array([float(r["eta_minutes"]) for r in rows], dtype=np.float32)

    # Normalized inputs for Tier 1 BrowserEdgeMLP (3 features)
    # rain / 200.0, (eff_tide - 1.0) / 4.5, subsidence / 40.0
    x_edge = np.stack([
        np.clip(rain_inst / 200.0, 0.0, 1.0),
        np.clip((eff_tide - 1.0) / 4.5, 0.0, 1.0),
        np.clip(subsidence / 40.0, 0.0, 1.0)
    ], axis=1).astype(np.float32)

    # Normalized inputs for Tier 2 BackendDeepMLP (5 features)
    # rain / 200.0, rain_1hr / 200.0, (pressure - 960.0) / 65.0, (eff_tide - 1.0) / 4.5, subsidence / 40.0
    x_backend = np.stack([
        np.clip(rain_inst / 200.0, 0.0, 1.0),
        np.clip(rain_1hr / 200.0, 0.0, 1.0),
        np.clip((pressure - 960.0) / 65.0, 0.0, 1.0),
        np.clip((eff_tide - 1.0) / 4.5, 0.0, 1.0),
        np.clip(subsidence / 40.0, 0.0, 1.0)
    ], axis=1).astype(np.float32)

    # Normalized target: eta / 180.0
    y_target = np.clip((eta / 180.0).reshape(-1, 1), 0.0, 1.0).astype(np.float32)

    return {
        "x_edge": torch.tensor(x_edge, dtype=torch.float32).to(DEVICE),
        "x_backend": torch.tensor(x_backend, dtype=torch.float32).to(DEVICE),
        "y": torch.tensor(y_target, dtype=torch.float32).to(DEVICE),
        "raw_eta": eta,
        "n_samples": len(rows)
    }


def export_browser_weights(model: BrowserEdgeMLP, filepath: str):
    """
    Exports serialized 209-param BrowserEdgeMLP weights to JSON.
    """
    sd = model.state_dict()
    payload = {
        "model_type": "BrowserEdgeMLP_209_PARAMS",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "param_count": 209,
        "input_features": ["rain_instant_norm_200", "effective_tide_norm_4_5", "subsidence_norm_40"],
        "target": "eta_inundation_norm_180",
        "W1": sd["net.0.weight"].cpu().numpy().tolist(),
        "b1": sd["net.0.bias"].cpu().numpy().tolist(),
        "W2": sd["net.2.weight"].cpu().numpy().tolist(),
        "b2": sd["net.2.bias"].cpu().numpy().tolist(),
        "W3": sd["net.4.weight"].cpu().numpy().tolist(),
        "b3": sd["net.4.bias"].cpu().numpy().tolist(),
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"  [OK] Exported BrowserEdgeMLP weights -> {filepath}")

    # Synchronize to frontend if folder exists
    if os.path.exists(FRONTEND_DATA_DIR):
        dest = os.path.join(FRONTEND_DATA_DIR, "weights_browser.json")
        shutil.copy2(filepath, dest)
        print(f"  [OK] Synchronized to frontend: {dest}")


def export_backend_weights(model: BackendDeepMLP, filepath: str):
    """
    Exports serialized 737-param BackendDeepMLP weights to JSON.
    """
    sd = model.state_dict()
    payload = {
        "model_type": "BackendDeepMLP_737_PARAMS",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "param_count": 737,
        "input_features": [
            "rain_instant_norm_200",
            "rain_1hr_norm_200",
            "pressure_norm_960_65",
            "effective_tide_norm_4_5",
            "subsidence_norm_40"
        ],
        "target": "eta_inundation_norm_180",
        "W1": sd["net.0.weight"].cpu().numpy().tolist(),
        "b1": sd["net.0.bias"].cpu().numpy().tolist(),
        "W2": sd["net.2.weight"].cpu().numpy().tolist(),
        "b2": sd["net.2.bias"].cpu().numpy().tolist(),
        "W3": sd["net.4.weight"].cpu().numpy().tolist(),
        "b3": sd["net.4.bias"].cpu().numpy().tolist(),
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"  [OK] Exported BackendDeepMLP weights -> {filepath}")

    # Synchronize to backend folders if they exist
    for target_dir in [BACKEND_LOCAL_DATA_DIR, BACKEND_CLOUD_DATA_DIR]:
        if os.path.exists(target_dir):
            dest = os.path.join(target_dir, "weights_backend.json")
            shutil.copy2(filepath, dest)
            print(f"  [OK] Synchronized to backend: {dest}")


def train_pipeline(epochs: int = 500, log_interval: int = 50):
    print("\n" + "=" * 78)
    print(" PROJECT FLOODLOCK // GATE 1 DUAL NEURAL NETWORK TRAINING SENTINEL")
    print(" Target Precinct: Mumbai F-South Ward (Hindmata & Love Grove)")
    print(f" Compute Device: {DEVICE}")
    print("=" * 78)

    # 1. Enforce dataset existence
    if not os.path.exists(TRAIN_CSV) or not os.path.exists(HOLDOUT_CSV):
        print("[!] Datasets missing. Initiating physics data synthesis...")
        generate_all()

    print("[*] Loading telemetry datasets into memory...")
    train_data = load_telemetry_csv(TRAIN_CSV)
    holdout_data = load_telemetry_csv(HOLDOUT_CSV)

    print(f"  [OK] Train Dataset:   {train_data['n_samples']} records loaded from {os.path.basename(TRAIN_CSV)}")
    print(f"  [OK] Holdout Dataset: {holdout_data['n_samples']} records loaded from {os.path.basename(HOLDOUT_CSV)}")

    # 2. Strict Model Parameter Count Assertions
    print("\n[*] Auditing model architectures and parameter counts...")
    p_edge, p_deep = verify_parameter_counts()
    print(f"  [OK] BrowserEdgeMLP: {p_edge} parameters (Required: 209) — PASS")
    print(f"  [OK] BackendDeepMLP: {p_deep} parameters (Required: 737) — PASS")

    loss_fn = nn.HuberLoss(delta=1.0)

    # -------------------------------------------------------------------------
    # STEP A: Train BrowserEdgeMLP (209 Parameters) — Trained FIRST
    # -------------------------------------------------------------------------
    print("\n" + "-" * 78)
    print(" [STEP 1/2] TRAINING TIER-1 BROWSER EDGE MLP (209 PARAMETERS — TRAINED FIRST)")
    print(" Input Features: [Rain_Instant, Effective_Tide, Subsidence]")
    print("-" * 78)

    edge_model = BrowserEdgeMLP().to(DEVICE)
    edge_opt = optim.Adam(edge_model.parameters(), lr=0.005, weight_decay=1e-5)
    edge_start = time.time()

    print(f"{'Epoch':<10} | {'Train Huber Loss':<18} | {'Holdout Huber Loss':<19} | {'Holdout MAE (Min)':<18}")
    print("-" * 78)

    for ep in range(1, epochs + 1):
        edge_model.train()
        edge_opt.zero_grad()
        preds_train = edge_model(train_data["x_edge"])
        loss_train = loss_fn(preds_train, train_data["y"])
        loss_train.backward()
        edge_opt.step()

        if ep == 1 or ep % log_interval == 0 or ep == epochs:
            edge_model.eval()
            with torch.no_grad():
                preds_holdout = edge_model(holdout_data["x_edge"])
                loss_holdout = loss_fn(preds_holdout, holdout_data["y"])
                mae_minutes = torch.mean(torch.abs((preds_holdout - holdout_data["y"]) * 180.0)).item()

            print(f"Epoch {ep:<4}/{epochs} | {loss_train.item():<18.6f} | {loss_holdout.item():<19.6f} | {mae_minutes:<18.2f}")

    edge_elapsed = time.time() - edge_start
    print(f"[OK] Tier-1 BrowserEdgeMLP trained in {edge_elapsed:.2f}s | Final Holdout MAE: {mae_minutes:.2f} min")

    # Save Edge Checkpoint & Weights
    torch.save(edge_model.state_dict(), os.path.join(CHECKPOINT_DIR, "browser_209_final.pt"))
    browser_weights_path = os.path.join(EXPORT_DIR, "weights_browser.json")
    export_browser_weights(edge_model, browser_weights_path)

    # -------------------------------------------------------------------------
    # STEP B: Train BackendDeepMLP (737 Parameters) — Trained SECOND
    # -------------------------------------------------------------------------
    print("\n" + "-" * 78)
    print(" [STEP 2/2] TRAINING TIER-2 BACKEND DEEP MLP (737 PARAMETERS — TRAINED SECOND)")
    print(" Input Features: [Rain_Instant, Rain_1hr, Pressure, Effective_Tide, Subsidence]")
    print("-" * 78)

    deep_model = BackendDeepMLP().to(DEVICE)
    deep_opt = optim.Adam(deep_model.parameters(), lr=0.005, weight_decay=1e-5)
    deep_start = time.time()

    print(f"{'Epoch':<10} | {'Train Huber Loss':<18} | {'Holdout Huber Loss':<19} | {'Holdout MAE (Min)':<18}")
    print("-" * 78)

    for ep in range(1, epochs + 1):
        deep_model.train()
        deep_opt.zero_grad()
        preds_train = deep_model(train_data["x_backend"])
        loss_train = loss_fn(preds_train, train_data["y"])
        loss_train.backward()
        deep_opt.step()

        if ep == 1 or ep % log_interval == 0 or ep == epochs:
            deep_model.eval()
            with torch.no_grad():
                preds_holdout = deep_model(holdout_data["x_backend"])
                loss_holdout = loss_fn(preds_holdout, holdout_data["y"])
                mae_minutes = torch.mean(torch.abs((preds_holdout - holdout_data["y"]) * 180.0)).item()

            print(f"Epoch {ep:<4}/{epochs} | {loss_train.item():<18.6f} | {loss_holdout.item():<19.6f} | {mae_minutes:<18.2f}")

    deep_elapsed = time.time() - deep_start
    print(f"[OK] Tier-2 BackendDeepMLP trained in {deep_elapsed:.2f}s | Final Holdout MAE: {mae_minutes:.2f} min")

    # Save Deep Checkpoint & Weights
    torch.save(deep_model.state_dict(), os.path.join(CHECKPOINT_DIR, "backend_737_final.pt"))
    backend_weights_path = os.path.join(EXPORT_DIR, "weights_backend.json")
    export_backend_weights(deep_model, backend_weights_path)

    print("\n" + "=" * 78)
    print(" [OK] GATE 1 TRAINING EXECUTION COMPLETE & ALL WEIGHTS EXPORTED")
    print(f"     Browser Weights: {browser_weights_path}")
    print(f"     Backend Weights: {backend_weights_path}")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    train_pipeline(epochs=500, log_interval=50)
