"""Do the glossary's Sinhala names match how the FLORES translators wrote them?"""
import re
import sys

import sinling

from common import flores, read_jsonl
from translate import load_glossary, match_terms

plain = lambda t: sinling.normalize(t, preset='search')
glossary = load_glossary()
src, ref = flores('devtest')
limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(src)
base = {r['id']: r['hyp'] for r in read_jsonl(sys.argv[2])} if len(sys.argv) > 2 else {}
agree = disagree = base_agree = 0
examples = []
for i in range(limit):
    for phrase, entries in match_terms(src[i], glossary):
        forms = [plain(si) for si, _, _ in entries]
        stems = [''.join(sinling.aksharas(f)[:-1]) or f for f in forms]
        in_ref = any(s and s in plain(ref[i]) for s in stems)
        agree += in_ref
        disagree += not in_ref
        if i in base:
            base_agree += any(s and s in plain(base[i]) for s in stems)
        if not in_ref and len(examples) < 8:
            examples.append((phrase, entries[0][0]))
total = agree + disagree
print(f'{total} glossary terms in {limit} sentences: the reference uses the glossary form for {agree} ({agree / total:.0%})')
if base:
    print(f'the plain-prompt translation already used the glossary form for {base_agree} ({base_agree / total:.0%})')
print('examples where the reference differs:', examples)

latin = [len(re.findall(r'[A-Za-z]{2,}', r)) for r in ref[:limit]]
print(f'references containing Latin-script words: {sum(1 for n in latin if n)} of {limit}')
