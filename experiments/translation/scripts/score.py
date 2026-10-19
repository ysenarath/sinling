"""Score translation runs with chrF++ (sacrebleu), after Sinling's normalize() on both sides.

For each run with a matching 'base' run of the same model and size, a paired bootstrap (1,000
resamples of the sentences) gives a 95% confidence interval for the difference from base.

Usage: python score.py [RUN.jsonl ...]   (default: every run under data/runs)
"""

import random
import sys
from pathlib import Path

import sacrebleu
import sinling

from common import RUNS, read_jsonl


CHRF = sacrebleu.metrics.CHRF(word_order=2)


def chrf(hyps, refs):
    return CHRF.corpus_score(hyps, [refs]).score


def _stats(hyps, refs):
    """Per-sentence chrF++ counts, so a resample's score is just a sum of counts."""
    return CHRF._extract_corpus_statistics(hyps, [refs])


def _score(stats, idx):
    total = [sum(stats[i][k] for i in idx) for k in range(len(stats[0]))]
    return CHRF._compute_score_from_stats(total).score


def bootstrap_diff(hyps, base_hyps, refs, resamples=1000, seed=0):
    """95% interval of chrF++(hyps) - chrF++(base_hyps) over resampled sentence sets."""
    rng = random.Random(seed)
    a, b = _stats(hyps, refs), _stats(base_hyps, refs)
    n, diffs = len(refs), []
    for _ in range(resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(_score(a, idx) - _score(b, idx))
    diffs.sort()
    return diffs[int(0.025 * resamples)], diffs[int(0.975 * resamples) - 1]


def main():
    paths = [Path(p) for p in sys.argv[1:]] or sorted(RUNS.rglob('*.jsonl'))
    print('| Model | Setup | Sentences | chrF++ | vs base (95% CI) | Cost (USD) |')
    print('| --- | --- | --- | --- | --- | --- |')
    norm = lambda xs: [sinling.normalize(x) for x in xs]
    for path in paths:
        rows = sorted(read_jsonl(path), key=lambda r: r['id'])
        hyps, refs = norm([r['hyp'] for r in rows]), norm([r['ref'] for r in rows])
        score = chrf(hyps, refs)
        base_path = path.with_name('base_' + path.stem.split('_', 1)[1] + '.jsonl')
        diff = ''
        if base_path != path and base_path.exists():
            base = sorted(read_jsonl(base_path), key=lambda r: r['id'])
            if [r['id'] for r in base] == [r['id'] for r in rows]:
                base_hyps = norm([r['hyp'] for r in base])
                low, high = bootstrap_diff(hyps, base_hyps, refs)
                diff = f'{score - chrf(base_hyps, refs):+.1f} ({low:+.1f} to {high:+.1f})'
        model = path.parent.name.replace('__', '/')
        print(f'| {model} | {path.stem} | {len(rows)} | {score:.1f} | {diff} | {sum(r["cost"] for r in rows):.4f} |')


if __name__ == '__main__':
    main()
