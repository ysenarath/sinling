#!/bin/bash
# Pilot: each teacher model translates the 997 FLORES dev sentences, one model at a time on one GPU.
# Submit from the experiments/ folder on Hopper: sbatch distillation/hopper/pilot.sbatch
#SBATCH --job-name=si-teachers
#SBATCH --partition=gpuq
#SBATCH --qos=gpu
#SBATCH --gres=gpu:A100.80gb:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=0-04:00:00
#SBATCH --output=distillation/logs/%x-%j.out

source distillation/hopper/env.sh
export HF_HUB_OFFLINE=1  # models were downloaded by setup.sh
export VLLM_USE_FLASHINFER_SAMPLER=0  # translation is greedy, so skip compiling a sampling kernel
PORT=$((20000 + SLURM_JOB_ID % 20000))
LD_LIBRARY_PATH=/usr/local/lib nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv || true

for model in $TEACHERS; do
    log=distillation/logs/vllm-$SLURM_JOB_ID-${model//\//__}.log
    echo "== $model ($(date +%T))"
    # shellcheck disable=SC2046
    "$VENV/bin/vllm" serve "$model" --served-model-name "$model" --port "$PORT" --max-model-len 4096 --gpu-memory-utilization 0.92 \
        $(serve_flags "$model") > "$log" 2>&1 &
    server=$!
    ready=0
    for _ in $(seq 360); do  # up to 30 minutes to load
        if curl -sf "http://127.0.0.1:$PORT/health" > /dev/null; then ready=1; break; fi
        kill -0 $server 2> /dev/null || break
        sleep 5
    done
    if [ $ready = 1 ]; then
        echo "server ready ($(date +%T))"
        "$VENV/bin/python" distillation/scripts/teachers.py "$model" --split dev --port "$PORT" \
            || echo "translation failed for $model"
    else
        echo "server failed to start for $model; last lines of $log:"
        tail -20 "$log"
    fi
    kill $server 2> /dev/null
    wait $server 2> /dev/null
done
echo "done ($(date +%T))"
