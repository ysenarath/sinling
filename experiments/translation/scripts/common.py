"""Paths and small helpers shared by the translation experiment scripts."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
FLORES = DATA / 'flores'
GLOSSARY = DATA / 'glossary'
RUNS = DATA / 'runs'

FLORES_SHA256 = 'b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6'

# Common English words that are never glossary terms on their own.
STOPWORDS = set('''
a about above after again against all also am an and any are as at be because been before being below
between both but by can could did do does doing down during each few for from further had has have having
he her here hers herself him himself his how i if in into is it its itself just me more most my myself no
nor not now of off on once only or other our ours ourselves out over own same she should so some such than
that the their theirs them themselves then there these they this those through to too under until up very
was we were what when where which while who whom why will with would you your yours yourself yourselves
said says one two three new many much may might must also however although though since than per via
'''.split())

WORD = re.compile(r"[A-Za-z][A-Za-z'\-]*")


def read_lines(path):
    return path.read_text(encoding='utf-8').rstrip('\n').split('\n')


def flores(split):
    """English and Sinhala sentences of FLORES-200 'dev' or 'devtest', aligned by line."""
    return read_lines(FLORES / f'{split}.en'), read_lines(FLORES / f'{split}.si')


def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def phrases(sentence, max_words=4):
    """Candidate glossary phrases: 1 to max_words word n-grams that don't start or end with a stopword."""
    words = WORD.findall(sentence)
    out = set()
    for n in range(1, max_words + 1):
        for i in range(len(words) - n + 1):
            gram = words[i:i + n]
            if gram[0].lower() in STOPWORDS or gram[-1].lower() in STOPWORDS:
                continue
            if n == 1 and len(gram[0]) < 3:
                continue
            out.add(' '.join(gram))
    return out
