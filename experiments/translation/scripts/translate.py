"""Translate FLORES English into Sinhala with an LLM under five setups.

    base      the sentence alone
    glossary  + matching glossary terms (Wikidata, Wiktionary)
    examples  + the most similar FLORES dev sentence pairs (BM25)
    both      + glossary and examples
    checks    both, then automatic checks alone drive up to two revisions
    review    both, then automatic checks and a grammar review drive up to two revisions

Usage: python translate.py MODEL SETUP [--split devtest] [--limit N] [--workers 8]
"""

import argparse
import json
import math
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import sinling

from common import GLOSSARY, RUNS, STOPWORDS, WORD, flores, read_jsonl, write_jsonl
from openrouter import BudgetExceeded, chat

SETUPS = ('base', 'glossary', 'examples', 'both', 'checks', 'review')
MAX_TERMS, N_EXAMPLES, MAX_ROUNDS = 8, 4, 2

SYSTEM = ('You are a professional English-to-Sinhala translator. Translate the English text into natural, '
          'accurate written Sinhala, as used in Sri Lankan newspapers. Keep every piece of meaning and every '
          'number. Write names in Sinhala script. Output only the Sinhala translation.')

# Draft checklist for the grammar review; to be reviewed by a native speaker.
CHECKLIST = '''1. The register is written Sinhala throughout, not spoken forms (e.g. "කරයි", not "කරනවා").
2. Verbs agree with their subject in person and number (මම ...මි, අපි ...මු, ඔහු ...යි / ...ය).
3. Case endings and postpositions are correct (ට, ගේ, ගෙන්, තුළ, විසින්, සමඟ).
4. Nothing from the English is missing or added; names and numbers are carried over correctly.
5. Word order and punctuation read naturally in Sinhala; quotation marks match the English.'''


# ---------- glossary ----------

def load_glossary():
    exact, lower = {}, {}
    for row in read_jsonl(GLOSSARY / 'wikidata_en_si.jsonl'):
        if '(' in row['si']:  # a bracketed note marks one specific sense, e.g. the chess queen
            continue
        exact.setdefault(row['en'], []).append((row['si'], '', 'wikidata'))
    for row in read_jsonl(GLOSSARY / 'wiktionary_en_si.jsonl'):
        if row['en'].lower() in STOPWORDS:
            continue
        note = (row.get('sense') or '')[:40]
        entries = lower.setdefault(row['en'].lower(), [])
        if all(si != row['si'] for si, _, _ in entries) and len(entries) < 3:
            entries.append((row['si'], note, 'wiktionary'))
    return exact, lower


def _name_runs(words):
    """Index ranges of runs of capitalized words, e.g. "Dalhousie University" or "Shark Tank"."""
    runs, start = [], None
    for i, word in enumerate(words + ['x']):
        if word[0].isupper() and i < len(words):
            start = i if start is None else start
        elif start is not None:
            runs.append((start, i))
            start = None
    return runs


def match_terms(sentence, glossary):
    """Glossary entries for names and multi-word terms in the sentence.

    Single lowercase words are skipped (the model knows them, and the glossary's sense is often
    wrong), and so is a single word that is only part of a longer name (Shark in "Shark Tank").
    """
    exact, lower = glossary
    words = WORD.findall(sentence)
    in_longer_name = set()
    for start, end in _name_runs(words):
        if end - start > 1:
            in_longer_name.update(range(start, end))
    used, terms = [False] * len(words), []
    for n in range(4, 0, -1):
        for i in range(len(words) - n + 1):
            if any(used[i:i + n]):
                continue
            gram = words[i:i + n]
            if gram[0].lower() in STOPWORDS or gram[-1].lower() in STOPWORDS or (n == 1 and len(gram[0]) < 3):
                continue
            phrase = ' '.join(gram)
            if n == 1 and (i == 0 or not gram[0][0].isupper() or i in in_longer_name):
                continue  # a common word, a sentence-initial word, or a fragment of a longer name
            # A single word must be a name as written; a multi-word term may also match in lowercase.
            entries = list(exact.get(phrase) or ([] if n == 1 else exact.get(phrase.lower(), [])))
            entries += [e for e in lower.get(phrase.lower(), []) if all(e[0] != have[0] for have in entries)]
            if entries:
                terms.append((phrase, entries))
                used[i:i + n] = [True] * n
    return terms[:MAX_TERMS]


def glossary_text(terms):
    lines = []
    for phrase, entries in terms:
        options = ' / '.join(si + (f' ({note})' if note else '') for si, note, _ in entries)
        lines.append(f'- {phrase} → {options}')
    return 'Glossary (use these Sinhala terms where they fit the meaning):\n' + '\n'.join(lines)


# ---------- example retrieval (BM25 over FLORES dev English) ----------

class BM25:
    def __init__(self, documents, k1=1.5, b=0.75):
        self.docs = [self._tokens(d) for d in documents]
        self.avg = sum(map(len, self.docs)) / len(self.docs)
        df = Counter(t for d in self.docs for t in set(d))
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.tf = [Counter(d) for d in self.docs]
        self.k1, self.b = k1, b

    @staticmethod
    def _tokens(text):
        return [w.lower() for w in WORD.findall(text) if w.lower() not in STOPWORDS]

    def top(self, query, k):
        q = self._tokens(query)
        scores = []
        for i, (tf, doc) in enumerate(zip(self.tf, self.docs)):
            norm = self.k1 * (1 - self.b + self.b * len(doc) / self.avg)
            scores.append((sum(self.idf.get(t, 0) * tf[t] * (self.k1 + 1) / (tf[t] + norm) for t in q if t in tf), i))
        return [i for score, i in sorted(scores, reverse=True)[:k] if score > 0]


def examples_text(indices, dev_en, dev_si):
    pairs = '\n\n'.join(f'English: {dev_en[i]}\nSinhala: {dev_si[i]}' for i in reversed(indices))
    return 'Examples of similar sentences and their Sinhala translations:\n\n' + pairs


# ---------- prompts ----------

def translation_messages(sentence, context):
    parts = context + [f'Translate into Sinhala:\n{sentence}']
    return [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': '\n\n'.join(parts)}]


def review_messages(sentence, translation):
    return [
        {'role': 'system', 'content': 'You are a careful Sinhala editor reviewing a translation from English.'},
        {'role': 'user', 'content': (
            f'English:\n{sentence}\n\nSinhala translation:\n{translation}\n\nCheck the translation against this '
            f'checklist:\n{CHECKLIST}\n\nReply with JSON only: {{"issues": ["..."]}}, listing at most 5 specific '
            'problems (quote the Sinhala words concerned). Use an empty list if the translation is good.')},
    ]


def revision_messages(sentence, translation, issues, context):
    problems = '\n'.join(f'- {issue}' for issue in issues)
    parts = context + [f'English:\n{sentence}', f'Current Sinhala translation:\n{translation}',
                       f'Problems found:\n{problems}',
                       'Write the corrected Sinhala translation. Output only the translation.']
    return [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': '\n\n'.join(parts)}]


# ---------- automatic checks ----------

_JOINERS = str.maketrans('', '', '\N{ZERO WIDTH JOINER}\N{ZERO WIDTH NON-JOINER}')
_NUMBER = re.compile(r'\d+(?:[.,:]\d+)*')
_LATIN_WORD = re.compile(r'[A-Za-z]{2,}')
_SINHALA = re.compile(f'[{chr(0x0D81)}-{chr(0x0DF4)}]')


def _plain(text):
    return sinling.normalize(text).translate(_JOINERS)


def automatic_checks(sentence, translation, terms):
    issues = []
    if not _SINHALA.search(translation):
        return ['The output is not in Sinhala.']
    for number in _NUMBER.findall(sentence):
        if number not in translation:
            issues.append(f'The number {number} from the English is missing.')
    for word in sorted(set(_LATIN_WORD.findall(translation))):
        if sum(c.isupper() for c in word) >= 2:
            continue  # acronyms and brand names (NSA, ZMapp) are often kept in Latin script
        issues.append(f'"{word}" is left in English; translate it or write it in Sinhala script.')
    plain = _plain(translation)
    for phrase, entries in terms:
        stems = []
        for si, _, _ in entries:
            pieces = sinling.aksharas(_plain(si))
            stems.append(''.join(pieces[:-1]) if len(pieces) >= 3 else ''.join(pieces))
        if not any(stem and stem in plain for stem in stems):
            issues.append(f'The glossary gives "{entries[0][0]}" for "{phrase}", but it is not used.')
    ratio = len(translation) / max(len(sentence), 1)
    if not 0.5 <= ratio <= 2.2:
        issues.append(f'The translation looks too {"short" if ratio < 0.5 else "long"} for the English.')
    return issues


def parse_issues(reply):
    match = re.search(r'\{.*\}', reply, re.S)
    try:
        issues = json.loads(match.group())['issues'] if match else []
    except (json.JSONDecodeError, KeyError, TypeError):
        return []
    return [str(i) for i in issues][:5] if isinstance(issues, list) else []


# ---------- one sentence ----------

def translate_one(model, setup, sentence, glossary, bm25, dev):
    context, terms = [], []
    if setup in ('glossary', 'both', 'checks', 'review'):
        terms = match_terms(sentence, glossary)
        if terms:
            context.append(glossary_text(terms))
    if setup in ('examples', 'both', 'checks', 'review'):
        context.append(examples_text(bm25.top(sentence, N_EXAMPLES), *dev))

    text, cost, _ = chat(model, translation_messages(sentence, context))
    record = {'terms': [p for p, _ in terms], 'rounds': []}
    if setup not in ('checks', 'review'):
        return text, cost, record

    candidates = []
    for round_ in range(MAX_ROUNDS + 1):
        auto = automatic_checks(sentence, text, terms)
        review = []
        if setup == 'review':
            reply, c, _ = chat(model, review_messages(sentence, text), max_tokens=600)
            cost += c
            review = parse_issues(reply)
        score = 2 * len(auto) + len(review)
        candidates.append((score, round_, text))
        record['rounds'].append({'text': text, 'automatic': auto, 'review': review})
        if score == 0 or round_ == MAX_ROUNDS:
            break
        text, c, _ = chat(model, revision_messages(sentence, text, auto + review, context))
        cost += c
    best = min(candidates)
    record['chosen_round'] = best[1]
    return best[2], cost, record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model')
    parser.add_argument('setup', choices=SETUPS)
    parser.add_argument('--split', default='devtest', choices=('dev', 'devtest'))
    parser.add_argument('--limit', type=int)
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    if args.split == 'dev' and args.setup in ('examples', 'both', 'checks', 'review'):
        parser.error('examples come from dev, so these setups must be run on devtest')

    src, ref = flores(args.split)
    src, ref = src[:args.limit], ref[:args.limit]
    dev = flores('dev')
    glossary = load_glossary() if args.setup in ('glossary', 'both', 'checks', 'review') else None
    bm25 = BM25(dev[0]) if args.setup in ('examples', 'both', 'checks', 'review') else None

    def work(i):
        try:
            hyp, cost, record = translate_one(args.model, args.setup, src[i], glossary, bm25, dev)
        except BudgetExceeded:
            return None
        return {'id': i, 'src': src[i], 'ref': ref[i], 'hyp': hyp, 'cost': cost, **record}

    with ThreadPoolExecutor(args.workers) as pool:
        rows = list(pool.map(work, range(len(src))))
    done = [r for r in rows if r is not None]
    out = RUNS / args.model.replace('/', '__') / f'{args.setup}_{args.split}{"_" + str(args.limit) if args.limit else ""}.jsonl'
    write_jsonl(out, done)
    print(f'{args.model} {args.setup}: {len(done)}/{len(src)} sentences, ${sum(r["cost"] for r in done):.4f} '
          f'-> {out.relative_to(RUNS.parent.parent)}')
    if len(done) < len(src):
        print('stopped early: spending cap reached')


if __name__ == '__main__':
    main()
