"""Runs the Python examples in README.md and the documentation, so they can't drift from the code."""

import doctest
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'docs' / 'source'
PAGES = [ROOT / 'README.md', *sorted(SOURCE.rglob('*.md'))]
CODE_BLOCK = re.compile(r'^```.*?^```', re.M | re.S)


def load_tests(loader, tests, ignore):
    for page in PAGES:
        if page.exists():  # absent when the tests run from an sdist
            tests.addTests(doctest.DocFileSuite(str(page), module_relative=False, encoding='utf-8'))
    tests.addTests(loader.loadTestsFromTestCase(TranslationTest))
    return tests


class TranslationTest(unittest.TestCase):
    """Each English page has a Sinhala twin (page.si.md) with the same code blocks."""

    @unittest.skipUnless(SOURCE.exists(), 'documentation sources are not available')
    def test_sinhala_pages_match_english_code(self):
        english = [p for p in SOURCE.rglob('*.md') if not p.name.endswith('.si.md')]
        self.assertTrue(english)
        for page in english:
            twin = page.with_name(page.name[:-3] + '.si.md')
            with self.subTest(page=str(page.relative_to(SOURCE))):
                self.assertTrue(twin.exists(), f'{twin.name} is missing')
                self.assertEqual(CODE_BLOCK.findall(twin.read_text(encoding='utf-8')),
                                 CODE_BLOCK.findall(page.read_text(encoding='utf-8')))
