"""Runs the Python examples in README.md, so the README can't drift from the code."""

import doctest
from pathlib import Path

README = Path(__file__).resolve().parent.parent / 'README.md'


def load_tests(loader, tests, ignore):
    if README.exists():  # absent when the tests run from an sdist
        tests.addTests(doctest.DocFileSuite(str(README), module_relative=False, encoding='utf-8'))
    return tests
