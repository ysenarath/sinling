#!/bin/bash
# Each dedicated translation model translates the 997 FLORES dev sentences, one after another on one GPU.
# Submit from the experiments/ folder on Hopper: sbatch distillation/hopper/mt.sbatch
#SBATCH --job-name=si-mt
#SBATCH --partition=gpuq
#SBATCH --qos=gpu
#SBATCH --gres=gpu:A100.80gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=0-03:00:00
#SBATCH --output=distillation/logs/%x-%j.out

source distillation/hopper/env.sh
export HF_HUB_OFFLINE=1  # models were downloaded by setup_mt.sh
LD_LIBRARY_PATH=/usr/local/lib nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv || true

for model in $MT_MODELS; do
    echo "== $model ($(date +%T))"
    "$VENV/bin/python" distillation/scripts/mt_models.py "$model" --split dev || echo "translation failed for $model"
done
echo "done ($(date +%T))"
