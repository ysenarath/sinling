"""chrF++ difference between two runs of the same sentences, with a 95% bootstrap interval."""
import collections
import sys

import sinling

from common import read_jsonl
from score import bootstrap_diff, chrf

norm = lambda xs: [sinling.normalize(x) for x in xs]
a = sorted(read_jsonl(sys.argv[1]), key=lambda r: r['id'])
b = sorted(read_jsonl(sys.argv[2]), key=lambda r: r['id'])
ha, hb, refs = norm([r['hyp'] for r in a]), norm([r['hyp'] for r in b]), norm([r['ref'] for r in a])
low, high = bootstrap_diff(ha, hb, refs)
print(f'{sys.argv[1].split("/")[-1]} vs {sys.argv[2].split("/")[-1]}: {chrf(ha, refs) - chrf(hb, refs):+.1f} ({low:+.1f} to {high:+.1f})')
if a[0].get('rounds'):
    chosen = collections.Counter(r.get('chosen_round', 0) for r in a)
    flagged = sum(1 for r in a if r['rounds'][0]['automatic'] or r['rounds'][0]['review'])
    print(f'  sentences flagged in round 0: {flagged}/{len(a)}; final version came from round {dict(sorted(chosen.items()))}')
