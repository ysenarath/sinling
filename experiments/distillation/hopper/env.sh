# Paths and teacher models shared by the Hopper scripts.
WORK=/scratch/$USER/sinling-exp
VENV=$WORK/.venv
export HF_HOME=/scratch/$USER/hf
export UV_CACHE_DIR=/scratch/$USER/.cache/uv
export VLLM_CACHE_ROOT=/scratch/$USER/.cache/vllm
export FLASHINFER_WORKSPACE_BASE=/scratch/$USER/.cache
export TRITON_CACHE_DIR=/scratch/$USER/.cache/triton
# vLLM compiles some kernels on first start and needs ninja and nvcc from the environment.
export PATH=$VENV/bin:$PATH

# Permissively licensed (Apache-2.0 or MIT) models that fit on one 80 GB GPU.
TEACHERS="Qwen/Qwen3.8-27B openai/gpt-oss-120b zai-org/GLM-4.7-Flash mistralai/Ministral-3-14B-Instruct-2512"

# Dedicated translation models (encoder-decoder), run with transformers by mt_models.py.
MT_MODELS="google/madlad400-3b-mt google/madlad400-10b-mt facebook/m2m100_1.2B CohereLabs/aya-101 facebook/nllb-200-3.3B"

# Extra `vllm serve` flags for each model.
serve_flags() {
    case $1 in
        Qwen/*) echo "--reasoning-parser qwen3 --limit-mm-per-prompt {\"image\":0,\"video\":0}" ;;
        zai-org/*) echo "--reasoning-parser glm45" ;;
        mistralai/*) echo "--tokenizer-mode mistral --config-format mistral --load-format mistral --limit-mm-per-prompt {\"image\":0}" ;;
        *) echo "" ;;
    esac
}
