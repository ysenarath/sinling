import csv
import re
import unittest
from pathlib import Path

import sinling
from sinling import from_legacy_font, normalize, pipeline
from sinling.legacy_fonts import is_fm_font

DATA = Path(__file__).parent / 'data' / 'legacy_fm.tsv'
_ESCAPE = re.compile(r'\\(x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|\\)')


def unescape(text):
    return _ESCAPE.sub(lambda m: '\\' if m[1] == '\\' else chr(int(m[1][1:], 16)), text)


with DATA.open(encoding='utf-8', newline='') as f:
    SAMPLES = [(unescape(r['fm']), unescape(r['expected']))
               for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE)]


class FMConverterTest(unittest.TestCase):
    def test_samples(self):
        self.assertEqual(len(SAMPLES), 12)
        for fm, expected in SAMPLES:
            with self.subTest(fm=fm):
                self.assertEqual(from_legacy_font(fm, normalize=False), expected)
                self.assertEqual(from_legacy_font(fm), normalize(expected))

    def test_alignment_maps_back_to_the_fm_text(self):
        doc = pipeline(['legacy_font'])('jd;h frda.')
        self.assertEqual(doc.text, 'වාතය රෝග')
        self.assertEqual(doc.raw[slice(*doc.to_raw(0, 2))], 'jd')  # වා
        self.assertEqual(doc.raw[slice(*doc.to_raw(5, 7))], 'frda')  # රෝ: kombuva moved and composed
        for fm, _ in SAMPLES:
            doc = pipeline(['legacy_font'])(fm)
            starts = [doc.to_raw(i, len(doc.text))[0] for i in range(len(doc.text) + 1)]
            self.assertEqual(starts, sorted(starts))

    def test_unicode_sinhala_passes_through(self):
        self.assertEqual(from_legacy_font('ගෙදර 2026', normalize=False), 'ගෙදර 2026')

    def test_unmapped_characters_are_counted(self):
        doc = pipeline(['legacy_font'])('jd;h\N{EURO SIGN}\N{EURO SIGN}')
        self.assertEqual(doc.text, 'වාතය\N{EURO SIGN}\N{EURO SIGN}')
        self.assertEqual(doc.meta['legacy_font_unmapped'], {'\N{EURO SIGN}': 2})

    def test_control_characters_are_dropped(self):
        self.assertEqual(from_legacy_font('jd\x01;h'), 'වාතය')

    def test_pipeline_from_fm_to_tokens(self):
        doc = pipeline(['legacy_font', 'normalize', 'tokenize'])('fomd\xbe;f\xefka;=j iy jdylhka')
        self.assertEqual([t.text for t in doc.tokens], ['දෙපාර්තමේන්තුව', 'සහ', 'වාහකයන්'])
        self.assertEqual(doc.raw[slice(*doc.to_raw(doc.tokens[1]))], 'iy')

    def test_is_fm_font(self):
        for name in ('FMAbhaya', 'ABCDEF+FMMalithi', 'FMEmanee', 'SARAWIPULA', 'XYZ+Chamodi'):
            self.assertTrue(is_fm_font(name), name)
        for name in ('Iskoola Pota', 'ABCDEF+Arial', 'NotoSansSinhala'):
            self.assertFalse(is_fm_font(name), name)

    def test_registered(self):
        info = [(b.name, b.default, b.offline) for b in sinling.backends('legacy_font')]
        self.assertEqual(info, [('fm', True, True)])


if __name__ == '__main__':
    unittest.main()
