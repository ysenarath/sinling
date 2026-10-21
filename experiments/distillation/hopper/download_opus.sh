#!/bin/bash
# Download the OPUS English-Sinhala corpora for the data audit (about 1.8 GB) into $WORK.
# Run once on the login node. OpenSubtitles (copyrighted subtitles) and software strings are skipped.
set -euo pipefail
source "$(dirname "$0")/env.sh"
dest=$WORK/distillation/data/opus
mkdir -p "$dest"
for c in wikimedia/v20260327 WikiMatrix/v1 ParaCrawl/v9 CCAligned/v1 CCMatrix/v1 NLLB/v1; do
    name=${c%/*}
    [ -s "$dest/$name.en-si.zip" ] || curl -fsSL -o "$dest/$name.en-si.zip" \
        "https://object.pouta.csc.fi/OPUS-$name/${c#*/}/moses/en-si.txt.zip"
    echo "$name $(du -h "$dest/$name.en-si.zip" | cut -f1)"
done
