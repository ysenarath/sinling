"""Summarise what the glossary and the review loop did in a set of runs."""
import collections
import sys

import sacrebleu
import sinling

from common import read_jsonl

base = {r['id']: r for r in read_jsonl(sys.argv[1])}
for path in sys.argv[2:]:
    rows = read_jsonl(path)
    name = path.rsplit('/', 1)[-1]
    with_terms = [r for r in rows if r.get('terms')]
    print(f'== {name}: {len(with_terms)}/{len(rows)} sentences got glossary terms; '
          f'{sum(len(r["terms"]) for r in rows)} terms in total')
    search = lambda xs: [sinling.normalize(x, preset='search') for x in xs]
    for label, subset in (('all', rows), ('with terms', with_terms)):
        if not subset:
            continue
        hyp = sacrebleu.corpus_chrf(search([r['hyp'] for r in subset]), [search([r['ref'] for r in subset])], word_order=2).score
        b = sacrebleu.corpus_chrf(search([base[r['id']]['hyp'] for r in subset]), [search([r['ref'] for r in subset])], word_order=2).score
        print(f'   chrF++ ignoring joiners, {label}: {hyp:.1f} (base on same sentences: {b:.1f})')
    if rows and 'rounds' in rows[0] and rows[0]['rounds']:
        chosen = collections.Counter(r['chosen_round'] for r in rows)
        auto = collections.Counter(i.split(' ')[0] + ' ' + i.split(' ')[1] for r in rows for i in r['rounds'][0]['automatic'])
        print(f'   chosen round: {dict(sorted(chosen.items()))}; review issues in round 0: '
              f'{sum(len(r["rounds"][0]["review"]) for r in rows)}; automatic issues in round 0: {sum(auto.values())}')
        print('   automatic issue kinds:', auto.most_common(6))
        for r in [r for r in rows if r['rounds'][0]['review']][:3]:
            print('   review said:', r['rounds'][0]['review'][:2])
