#!/usr/bin/env bash
# The official recorded run: vault + full demo loop on NEAR mainnet, terminal recorded for the demo video.
#   RUN_ID=<id> AXON_LOCAL_STEPS=.. AXON_LR=.. ROUNDS=.. ./scripts/mainnet_run.sh
# Needs: mainnet keys for *.axon.ebukaa.near in ~/.near-credentials/mainnet, asciinema, a GPU.
set -euo pipefail
cd "$(dirname "$0")/.."
export AXON_NETWORK=mainnet AXON_CONTRACT=axon.ebukaa.near AXON_PARENT=axon.ebukaa.near CREATOR=creator.axon.ebukaa.near
export BUDGET=${BUDGET:-0.06}
export AXON_BASE_MODEL=${AXON_BASE_MODEL:-Qwen/Qwen2.5-1.5B-Instruct}
export AXON_LORA_TARGETS=${AXON_LORA_TARGETS:-q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj}
export AXON_LORA_RANK=${AXON_LORA_RANK:-16} AXON_MAX_LEN=${AXON_MAX_LEN:-384}
PY=${PY:-python}
export PY
RUN_ID=${RUN_ID:-$(date -u +%Y%m%d-%H%M)-mainnet-rtx4090}
export RUN_ID
mkdir -p "runs/$RUN_ID"
$PY -m axon vault --operator vault.axon.ebukaa.near > "runs/$RUN_ID/vault.log" 2>&1 &
VAULT=$!
trap 'kill $VAULT 2>/dev/null || true' EXIT
until curl -s -m 2 http://127.0.0.1:8700/info >/dev/null; do sleep 2; done
asciinema rec --overwrite -q -i 2 -c "nvidia-smi; echo; ./scripts/run.sh" "runs/$RUN_ID/terminal.cast"
