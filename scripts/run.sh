#!/usr/bin/env bash
# A published training run: runs the full demo loop and saves everything to runs/<id>/, listed in RUNS.md.
#   ./scripts/run.sh                    # laptop (CPU) defaults
#   AXON_BASE_MODEL=Qwen/Qwen2.5-1.5B-Instruct AXON_LOCAL_STEPS=60 AXON_MAX_LEN=384 ./scripts/run.sh   # GPU
# Prereqs: the vault is running with the same AXON_* settings; AXON_CONTRACT and AXON_PARENT are set.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
DEV=$($PY -c "import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')" | tr ' ' '-' | tr -cd '[:alnum:]-' | tr '[:upper:]' '[:lower:]')
ID=${RUN_ID:-$(date -u +%Y%m%d-%H%M)-$DEV}
DIR=runs/$ID
$PY -m axon run-start --dir "$DIR"
T0=$(date +%s)
./scripts/demo.sh 2>&1 | tee "$DIR/log.txt"
MODEL=$(awk '/^model id:/{print $3}' "$DIR/log.txt")
$PY -m axon run-finish --dir "$DIR" --model "$MODEL" --seconds $(( $(date +%s) - T0 ))
