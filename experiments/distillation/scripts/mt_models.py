"""Translate FLORES English into Sinhala with a dedicated translation model (encoder-decoder).

The output has the same form as teachers.py, so the same scoring applies. Beam search with 4
beams, the usual setting for these models.

Usage: python mt_models.py MODEL [--split dev] [--limit N] [--batch-size 16]
"""

import argparse
import json
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / 'translation' / 'scripts'))

from common import flores, write_jsonl  # noqa: E402

RUNS = ROOT / 'data' / 'teachers'

# How each model is told to translate into Sinhala: a text prefix, or source and target language codes.
MODELS = {
    'google/madlad400-3b-mt': {'prefix': '<2si> '},
    'google/madlad400-10b-mt': {'prefix': '<2si> '},
    'CohereLabs/aya-101': {'prefix': 'Translate to Sinhala: '},
    'facebook/m2m100_418M': {'src_lang': 'en', 'tgt_token': '__si__'},  # for testing on a laptop
    'facebook/m2m100_1.2B': {'src_lang': 'en', 'tgt_token': '__si__'},
    'facebook/nllb-200-3.3B': {'src_lang': 'eng_Latn', 'tgt_token': 'sin_Sinh'},
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model', choices=MODELS)
    parser.add_argument('--split', default='dev', choices=('dev', 'devtest'))
    parser.add_argument('--limit', type=int)
    parser.add_argument('--batch-size', type=int, default=16)
    args = parser.parse_args()

    setup = MODELS[args.model]
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if 'src_lang' in setup:
        tokenizer.src_lang = setup['src_lang']
    model = AutoModelForSeq2SeqLM.from_pretrained(
        args.model, dtype=torch.bfloat16 if device == 'cuda' else torch.float32).to(device).eval()
    extra = {}
    if 'tgt_token' in setup:
        extra['forced_bos_token_id'] = tokenizer.convert_tokens_to_ids(setup['tgt_token'])

    src, ref = flores(args.split)
    src, ref = src[:args.limit], ref[:args.limit]
    hyps, tokens = [None] * len(src), [0] * len(src)
    order = sorted(range(len(src)), key=lambda i: len(src[i]))  # similar lengths batch with less padding

    start = time.monotonic()
    for b in range(0, len(order), args.batch_size):
        batch = order[b:b + args.batch_size]
        inputs = tokenizer([setup.get('prefix', '') + src[i] for i in batch], return_tensors='pt',
                           padding=True).to(device)
        with torch.inference_mode():
            out = model.generate(**inputs, num_beams=4, max_new_tokens=256, **extra)
        for i, ids in zip(batch, out):
            hyps[i] = tokenizer.decode(ids, skip_special_tokens=True).strip()
            tokens[i] = int((ids != tokenizer.pad_token_id).sum())
    seconds = time.monotonic() - start

    rows = [{'id': i, 'src': src[i], 'ref': ref[i], 'hyp': hyps[i], 'cost': 0.0, 'completion_tokens': tokens[i]}
            for i in range(len(src))]
    name = f'base_{args.split}{"_" + str(args.limit) if args.limit else ""}'
    out = RUNS / args.model.replace('/', '__') / f'{name}.jsonl'
    write_jsonl(out, rows)
    summary = {'model': args.model, 'sentences': len(rows), 'empty': sum(not h for h in hyps),
               'seconds': round(seconds, 1), 'completion_tokens': sum(tokens),
               'tokens_per_second': round(sum(tokens) / seconds, 1),
               'sentences_per_hour': round(len(rows) / seconds * 3600)}
    out.with_name(f'{name}.speed.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
