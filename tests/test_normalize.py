import csv
import random
import re
import unittest
from pathlib import Path

import sinling
from sinling import Doc, normalize, pipeline
from sinling.script import AL_LAKUNA, CONSONANTS, INDEPENDENT_VOWELS, VOWEL_SIGNS, ZWJ, ZWNJ

DATA = Path(__file__).parent / 'data' / 'normalize.tsv'
_ESCAPE = re.compile(r'\\(u[0-9a-fA-F]{4}|n|t)')


def unescape(text):
    return _ESCAPE.sub(lambda m: {'n': '\n', 't': '\t'}.get(m[1]) or chr(int(m[1][1:], 16)), text)


def load_cases():
    with DATA.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE))
    return [{**row, 'input': unescape(row['input']), 'expected': unescape(row['expected'])} for row in rows]


CASES = load_cases()


class GoldenCasesTest(unittest.TestCase):
    def test_cases_load(self):
        self.assertGreater(len(CASES), 40)
        self.assertEqual({c['rule'] for c in CASES} - {'all'},
                         {'invisible', 'doubled_signs', 'reorder', 'vowel_letters', 'zwj', 'nfc', 'whitespace'})

    def test_expected_output(self):
        for case in CASES:
            with self.subTest(note=case['note']):
                self.assertEqual(normalize(case['input'], case['preset']), case['expected'])

    def test_idempotent(self):
        for case in CASES:
            with self.subTest(note=case['note']):
                once = normalize(case['input'], case['preset'])
                self.assertEqual(normalize(once, case['preset']), once)

    def test_alignment_is_monotonic_and_in_bounds(self):
        for case in CASES:
            with self.subTest(note=case['note']):
                doc = pipeline([('normalize', 'rules', {'preset': case['preset']})])(case['input'])
                n = len(doc.text)
                previous = (0, 0)
                for i in range(n + 1):
                    start, end = doc.to_raw(i, n)
                    self.assertLessEqual(previous[0], start)
                    self.assertLessEqual(end, len(doc.raw))
                    previous = (start, end)
                for i in range(n):
                    start, end = doc.to_raw(i, i + 1)
                    self.assertLess(start, end, 'each output character comes from some input')


class RandomTextTest(unittest.TestCase):
    """Malformed input must still normalize idempotently with a valid alignment."""

    ALPHABET = (list(CONSONANTS) * 2 + list(INDEPENDENT_VOWELS) + list(VOWEL_SIGNS) * 2
                + [AL_LAKUNA] * 3 + [ZWJ] * 3 + [ZWNJ, chr(0x200b), chr(0xa0), ' ', '\n', 'a'])

    def test_random_strings(self):
        rng = random.Random(0)
        for _ in range(3000):
            text = ''.join(rng.choice(self.ALPHABET) for _ in range(rng.randint(0, 10)))
            for preset in ('standard', 'search'):
                doc = pipeline([('normalize', 'rules', {'preset': preset})])(text)
                with self.subTest(text=text, preset=preset):
                    self.assertEqual(normalize(doc.text, preset), doc.text)
                    starts = [doc.to_raw(i, len(doc.text))[0] for i in range(len(doc.text) + 1)]
                    self.assertEqual(starts, sorted(starts))


class OptionsTest(unittest.TestCase):
    def test_single_rules_can_be_turned_off(self):
        self.assertEqual(normalize('\u0dd9ග', reorder=False), '\u0dd9ග')
        self.assertEqual(normalize('ම\u200dම', zwj='keep'), 'ම\u200dම')
        self.assertEqual(normalize(' a  b ', whitespace='keep'), ' a  b ')
        self.assertEqual(normalize('ක\u200bර', invisible=False), 'ක\u200bර')

    def test_invalid_options(self):
        with self.assertRaisesRegex(TypeError, 'unknown normalize option'):
            normalize('x', zwnj='strip')
        with self.assertRaisesRegex(ValueError, 'unknown preset'):
            normalize('x', 'display')
        with self.assertRaisesRegex(ValueError, 'canonical, strip, keep'):
            normalize('x', zwj='remove')

    def test_doc_input_is_normalized_in_place(self):
        doc = Doc('\u0dd9කා ගම')
        self.assertEqual(normalize(doc), 'කො ගම')
        self.assertEqual(doc.text, 'කො ගම')
        self.assertEqual(doc.to_raw(0, 2), (0, 3))

    def test_registered_as_default_backend(self):
        info = sinling.backends('normalize')
        self.assertEqual([(b.name, b.default, b.offline) for b in info], [('rules', True, True)])

    def test_offsets_map_back_through_normalization(self):
        doc = pipeline(['normalize'])('\u200bමම\u00a0\u00a0\u0dd9ගදර')
        self.assertEqual(doc.text, 'මම ගෙදර')
        self.assertEqual(doc.raw[slice(*doc.to_raw(0, 2))], 'මම')
        self.assertEqual(doc.raw[slice(*doc.to_raw(3, 7))], '\u0dd9ගදර')


if __name__ == '__main__':
    unittest.main()
