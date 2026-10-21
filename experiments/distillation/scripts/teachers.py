"""Translate FLORES English into Sinhala with an open model served locally by vLLM.

Uses the same instructions and plain prompt as the translation experiment's 'base' setup, so the
results can be scored with its score.py. Also records how fast the model translates, to estimate
the GPU time for translating a large corpus.

Usage: python teachers.py MODEL [--split dev] [--limit N] [--port 8000] [--workers 64]
"""

import argparse
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / 'translation' / 'scripts'))

from common import flores, write_jsonl  # noqa: E402
from translate import translation_messages  # noqa: E402

RUNS = ROOT / 'data' / 'teachers'

# Turn off hidden reasoning where a model has a switch for it; gpt-oss can only be told to keep it short.
OPTIONS = {
    'openai/gpt-oss-120b': {'reasoning_effort': 'low'},
    'Qwen/Qwen3.8-27B': {'chat_template_kwargs': {'enable_thinking': False}},
    'zai-org/GLM-4.7-Flash': {'chat_template_kwargs': {'enable_thinking': False}},
}


def chat(port, model, messages, max_tokens=2048):
    body = {'model': model, 'messages': messages, 'max_tokens': max_tokens, 'temperature': 0.0,
            **OPTIONS.get(model, {})}
    request = urllib.request.Request(f'http://127.0.0.1:{port}/v1/chat/completions',
                                     data=json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=600) as response:
        data = json.load(response)
    message = data['choices'][0]['message']
    return (message.get('content') or '').strip(), data['usage']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model')
    parser.add_argument('--split', default='dev', choices=('dev', 'devtest'))
    parser.add_argument('--limit', type=int)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--workers', type=int, default=64)
    args = parser.parse_args()

    src, ref = flores(args.split)
    src, ref = src[:args.limit], ref[:args.limit]

    def work(i):
        hyp, usage = chat(args.port, args.model, translation_messages(src[i], []))
        return {'id': i, 'src': src[i], 'ref': ref[i], 'hyp': hyp, 'cost': 0.0,
                'prompt_tokens': usage['prompt_tokens'], 'completion_tokens': usage['completion_tokens']}

    start = time.monotonic()
    with ThreadPoolExecutor(args.workers) as pool:
        rows = list(pool.map(work, range(len(src))))
    seconds = time.monotonic() - start

    name = f'base_{args.split}{"_" + str(args.limit) if args.limit else ""}'
    out = RUNS / args.model.replace('/', '__') / f'{name}.jsonl'
    write_jsonl(out, rows)
    tokens = sum(r['completion_tokens'] for r in rows)
    summary = {'model': args.model, 'sentences': len(rows), 'empty': sum(not r['hyp'] for r in rows),
               'seconds': round(seconds, 1), 'completion_tokens': tokens,
               'tokens_per_second': round(tokens / seconds, 1),
               'sentences_per_hour': round(len(rows) / seconds * 3600)}
    out.with_name(f'{name}.speed.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
