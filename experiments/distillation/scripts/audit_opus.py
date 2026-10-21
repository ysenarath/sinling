"""Measure how much of each OPUS English-Sinhala corpus survives simple quality filters.

Reads the Moses-format zips downloaded by hopper/download_opus.sh, applies rule filters, removes
duplicates within and across corpora, drops any pair that overlaps FLORES-200, and writes:

    data/opus/audit.json        counts per corpus: pairs, duplicates, each filter's drops, survivors
    data/opus/filtered.tsv      the surviving pairs (en <TAB> si <TAB> corpus), for training only
    data/opus/sample.tsv        2,000 random survivors per corpus, to read and to score later

The filtered pairs are for training; they are not to be redistributed (see the README).

Usage: python audit_opus.py [--corpora NLLB CCMatrix ...]
"""

import argparse
import hashlib
import json
import random
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent / 'translation' / 'scripts'))

from common import flores  # noqa: E402

OPUS = ROOT / 'data' / 'opus'
CORPORA = ('wikimedia', 'WikiMatrix', 'ParaCrawl', 'CCAligned', 'CCMatrix', 'NLLB')
SAMPLE = 2000

SINHALA = re.compile('[඀-෿]')
LATIN = re.compile('[A-Za-z]')
LETTER = re.compile(r'[^\W\d_]')
DIGITS = re.compile(r'\d+')
URL = re.compile(r'https?://|www\.|@\w+\.')


CITATION = re.compile(r'\[\d+\]')  # Wikipedia footnote markers, e.g. [1]


def clean(text):
    return ' '.join(CITATION.sub('', unicodedata.normalize('NFC', text)).split())


def key(*parts):
    return hashlib.blake2b('\t'.join(parts).casefold().encode(), digest_size=8).digest()


def share(pattern, text):
    letters = LETTER.findall(text)
    return sum(bool(pattern.match(c)) for c in letters) / len(letters) if letters else 0.0


def length_bounds():
    """Sinhala/English character-length ratio range of FLORES (1st to 99th percentile), widened by 20%."""
    ratios = sorted(len(si) / len(en) for split in ('dev', 'devtest') for en, si in zip(*flores(split)))
    return ratios[len(ratios) // 100] * 0.8, ratios[len(ratios) * 99 // 100] * 1.2


def reason(en, si, low, high):
    """The first filter a pair fails, or None if it passes."""
    words = len(en.split())
    if words < 3:
        return 'too_short'
    if words > 150:
        return 'too_long'
    if URL.search(en) or URL.search(si):
        return 'url'
    if share(SINHALA, si) < 0.6:
        return 'si_not_sinhala'
    if share(LATIN, en) < 0.8:
        return 'en_not_english'
    if not low <= len(si) / len(en) <= high:
        return 'length_ratio'
    if Counter(DIGITS.findall(en)) != Counter(DIGITS.findall(si)):
        return 'numbers_differ'
    return None


def pairs(corpus):
    with zipfile.ZipFile(OPUS / f'{corpus}.en-si.zip') as z:
        names = {n.rsplit('.', 1)[-1]: n for n in z.namelist() if n.endswith(('.en', '.si'))}
        with z.open(names['en']) as fe, z.open(names['si']) as fs:
            for en, si in zip(fe, fs):
                yield clean(en.decode('utf-8', 'replace')), clean(si.decode('utf-8', 'replace'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpora', nargs='+', default=CORPORA)
    args = parser.parse_args()

    low, high = length_bounds()
    test = {key(clean(t)) for split in ('dev', 'devtest') for side in flores(split) for t in side}
    seen = set()
    rng = random.Random(0)
    # How often the filters would wrongly drop a good human translation.
    on_flores = Counter(reason(clean(en), clean(si), low, high) or 'kept'
                        for split in ('dev', 'devtest') for en, si in zip(*flores(split)))
    report = {'length_ratio_bounds': [round(low, 3), round(high, 3)], 'filters_on_flores': dict(on_flores),
              'corpora': {}}
    print('filters on FLORES:', dict(on_flores), flush=True)
    with open(OPUS / 'filtered.tsv', 'w', encoding='utf-8') as out, \
            open(OPUS / 'sample.tsv', 'w', encoding='utf-8') as sample_out:
        # Cleanest corpora first, so a pair found in several is credited to the cleanest one.
        for corpus in args.corpora:
            counts, sample, kept = Counter(), [], 0
            for en, si in pairs(corpus):
                counts['pairs'] += 1
                k = key(en, si)
                if k in seen:
                    counts['duplicate'] += 1
                    continue
                seen.add(k)
                if key(en) in test or key(si) in test:
                    counts['flores_overlap'] += 1
                    continue
                why = reason(en, si, low, high)
                if why:
                    counts[why] += 1
                    continue
                kept += 1
                out.write(f'{en}\t{si}\t{corpus}\n')
                # Reservoir sample, so the sample is uniform over all survivors.
                if len(sample) < SAMPLE:
                    sample.append((en, si))
                elif (j := rng.randrange(kept)) < SAMPLE:
                    sample[j] = (en, si)
            counts['kept'] = kept
            for en, si in sample:
                sample_out.write(f'{en}\t{si}\t{corpus}\n')
            report['corpora'][corpus] = dict(counts)
            print(corpus, json.dumps(dict(counts)), flush=True)
    (OPUS / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
