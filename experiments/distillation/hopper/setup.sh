#!/bin/bash
# One-time setup on the Hopper login node: a Python environment with vLLM, and the pilot's teacher
# models. Everything goes under /scratch, because the home quota is small. Safe to run again.
#
# Run from the experiments/ folder copied to Hopper: bash distillation/hopper/setup.sh
set -euo pipefail
source "$(dirname "$0")/env.sh"

mkdir -p "$WORK/distillation/logs" "$HF_HOME" "$UV_CACHE_DIR"
if [ ! -x "$VENV/bin/python" ]; then
    uv venv "$VENV" --python 3.12
fi
uv pip install --python "$VENV/bin/python" vllm==0.31.0 sacrebleu==2.5.1 "$WORK"/sinling-*-py3-none-any.whl

for model in $TEACHERS; do
    # gpt-oss also ships its original and Apple Metal weights, which vLLM doesn't need.
    "$VENV/bin/hf" download "$model" --exclude 'original/*' --exclude 'metal/*'
done
du -sh "$HF_HOME"
