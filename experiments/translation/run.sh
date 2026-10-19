#!/bin/sh
# Run an experiment script with Sinling (the wheel built into ../../dist) and sacrebleu.
# Example: ./run.sh translate.py deepseek/deepseek-v4.1-flash base --limit 50
cd "$(dirname "$0")" || exit 1
script=$1; shift
exec uv run --isolated --no-project --python 3.12 --with ../../dist/sinling-*-py3-none-any.whl \
    --with sacrebleu==2.5.1 python "scripts/$script" "$@"
