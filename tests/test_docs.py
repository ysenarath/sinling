"""Runs the Python examples in README.md and the documentation, so they can't drift from the code."""

import doctest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [ROOT / 'README.md', *sorted((ROOT / 'docs' / 'source').rglob('*.md'))]


def load_tests(loader, tests, ignore):
    for page in PAGES:
        if page.exists():  # absent when the tests run from an sdist
            tests.addTests(doctest.DocFileSuite(str(page), module_relative=False, encoding='utf-8'))
    return tests
