"""chrF++ of finished runs, without confidence intervals (fast)."""
import sys
import sacrebleu
import sinling
from common import read_jsonl
for path in sys.argv[1:]:
    rows = read_jsonl(path)
    norm = lambda xs: [sinling.normalize(x) for x in xs]
    score = sacrebleu.corpus_chrf(norm([r['hyp'] for r in rows]), [norm([r['ref'] for r in rows])], word_order=2).score
    print(f'{path.split("/")[-2]:32s} {path.split("/")[-1]:24s} {len(rows):5d}  chrF++ {score:.1f}')
