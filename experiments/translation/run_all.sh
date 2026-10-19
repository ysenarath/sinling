#!/bin/sh
# The full runs: four setups on three models, and the two revision setups on DeepSeek.
cd "$(dirname "$0")" || exit 1
for model in deepseek/deepseek-v4.1-flash google/gemini-2.5-flash-lite qwen/qwen3.7-flash; do
    for setup in base glossary examples both; do
        ./run.sh translate.py "$model" "$setup" || exit 1
    done
done
for setup in checks review; do
    ./run.sh translate.py deepseek/deepseek-v4.1-flash "$setup" || exit 1
done
cat data/spend.json
