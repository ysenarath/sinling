#!/bin/bash
# One-time setup for the translation models, on the Hopper login node, after setup.sh. Adds the
# tokenizer libraries they need and downloads the models (about 130 GB) to /scratch.
#
# Run from the experiments/ folder copied to Hopper: bash distillation/hopper/setup_mt.sh
set -euo pipefail
source "$(dirname "$0")/env.sh"

uv pip install --python "$VENV/bin/python" sentencepiece protobuf

for model in $MT_MODELS; do
    # Only the PyTorch weights and tokenizer files; the repos also hold Flax, TensorFlow and Rust copies.
    "$VENV/bin/hf" download "$model" --include '*.json' --include '*.model' --include '*.safetensors' \
        --include 'pytorch_model*.bin'
done
du -sh "$HF_HOME"
