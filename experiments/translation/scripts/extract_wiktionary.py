"""Keep English Wiktionary entries that have a Sinhala translation (reads kaikki.org JSONL on stdin).

Wiktionary content is licensed CC BY-SA 4.0; the output stays local and is not redistributed.
"""
import json
import sys



def sinhala_translations(node):
    """Yield every translation object marked Sinhala, wherever it is nested."""
    if isinstance(node, dict):
        if node.get('lang_code') == 'si' and node.get('word'):
            yield node
            return
        for value in node.values():
            yield from sinhala_translations(value)
    elif isinstance(node, list):
        for value in node:
            yield from sinhala_translations(value)


out = open(sys.argv[1], 'w', encoding='utf-8')
seen = kept = 0
for line in sys.stdin:
    seen += 1
    if '"lang_code": "si"' not in line:
        continue
    entry = json.loads(line)
    # Translations sit at the top level of some entries and inside senses in others.
    for t in sinhala_translations(entry):
        out.write(json.dumps({'en': entry['word'], 'pos': entry.get('pos'), 'sense': t.get('sense', ''),
                              'si': t['word']}, ensure_ascii=False) + '\n')
        kept += 1
print(f'read {seen} entries, kept {kept} Sinhala translations', file=sys.stderr)
