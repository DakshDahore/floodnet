#!/usr/bin/env bash
set -e
echo "=================================================================="
echo " PROJECT FLOODLOCK // NEURAL TRAINER PIPELINE"
echo "=================================================================="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "../.venv/bin/python" ]; then
    PYTHON_BIN="../.venv/bin/python"
elif [ -f ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN="python"
fi

# 1. Synthesize Physics Data
$PYTHON_BIN generate_datasets.py

# 2. Audit Model Parameter Counts
$PYTHON_BIN models.py

# 3. Train Dual Neural Networks and Export Real Weights
$PYTHON_BIN train_models.py

echo "=================================================================="
echo " [✓] ALL TRAINER PIPELINES COMPLETED SUCCESSFULLY"
echo "=================================================================="
