#!/usr/bin/env bash
# End-to-end Axon demo on NEAR (testnet or mainnet, set AXON_NETWORK):
#   create a model -> 4 contributors train locally on private data -> vault scores them (Shapley)
#   -> ownership recorded on-chain -> a user pays for a question -> owners earn.
#
# Prereqs: ./scripts/setup.sh done, vault running (`python -m axon vault --operator $OPERATOR`).
# Env: AXON_CONTRACT (contract account), AXON_PARENT (account the demo sub-accounts live under),
#      CREATOR (model creator, default AXON_PARENT), BUDGET (training budget in NEAR, default 0.2).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
: "${AXON_CONTRACT:?set AXON_CONTRACT}"
P=${AXON_PARENT:-$AXON_CONTRACT}
ROUNDS=${ROUNDS:-2}
CREATOR=${CREATOR:-$P}
BUDGET=${BUDGET:-0.2}
QUESTION=${QUESTION:-"Which gene is involved in Laing distal myopathy, and how is it inherited?"}
# Which demo model (default: the rare-disease health model). Other demos keep their data under data/<DOMAIN>/.
DOMAIN=${DOMAIN:-rare-diseases}
NAME=${NAME:-"Rare Disease Expert"}
DESCRIPTION=${DESCRIPTION:-"Answers questions about rare genetic diseases. Trained by specialist clinics and patient families on their own private data."}
CONTRIBUTORS=${CONTRIBUTORS:-"neuro-clinic metabolic-clinic alice bob"}
if [[ "$DOMAIN" == "rare-diseases" ]]; then CDIR=data/contributors; else CDIR=data/$DOMAIN/contributors; fi

echo "== 1. create the model (bound to the vault's key + code hash)"
if [[ -n "${MODEL:-}" ]]; then echo "reusing model $MODEL"; else
MODEL=$($PY -m axon create-model --creator "$CREATOR" --name "$NAME" --domain "$DOMAIN" --base-model "${AXON_BASE_MODEL:-}" \
  --description "$DESCRIPTION" \
  --price 0.01 --compute-fee 0.02 --budget "$BUDGET" | awk '/model/{print $2}'); fi
echo "model id: $MODEL"

for r in $(seq 1 "$ROUNDS"); do
  echo "== 2.$r contributors train locally and send sealed updates (round $r)"
  for who in $CONTRIBUTORS; do
    $PY -m axon contribute --model "$MODEL" --account "$who.$P" --data "$CDIR/$who.jsonl"
  done
  echo "== 3.$r vault merges, scores (Shapley) and records ownership on NEAR"
  $PY -m axon close-round --model "$MODEL" --compute-provider "gpu.$P"
done

echo "== 4. a user pays for a question; the payment is split among owners"
$PY -m axon ask --model "$MODEL" --account "user.$P" "$QUESTION"

echo "== 5. who owns the model, and what they earned"
$PY -m axon status --model "$MODEL"
