"""Shared test fixtures: an isolated registry with two toy tasks."""

import unittest

from sinling import Backend, Doc, Token, define_task, register
from sinling import registry


class Upper(Backend):
    """A text-changing toy backend."""

    def __call__(self, doc: Doc) -> Doc:
        doc.edit_text([(i, i + 1, c.upper()) for i, c in enumerate(doc.text) if c.islower()])
        return doc


class Whitespace(Backend):
    """A toy tokenizer that splits on spaces."""

    def __call__(self, doc: Doc) -> Doc:
        tokens, pos = [], 0
        for part in doc.text.split(' '):
            if part:
                tokens.append(Token(part, pos, pos + len(part)))
            pos += len(part) + 1
        doc.set_tokens(tokens)
        return doc


class RegistryTestCase(unittest.TestCase):
    """Gives each test a fresh registry with ``upper`` (changes text) and ``split`` tasks."""

    def setUp(self):
        self._saved = registry._registry
        registry._registry = registry._Registry()
        registry._registry._plugins = {}
        define_task('upper', lambda doc: doc.text, changes_text=True)
        define_task('split', lambda doc: [t.text for t in doc.tokens])
        register('upper', 'simple', default=True)(type('UpperSimple', (Upper,), {}))
        register('split', 'space', default=True)(type('SplitSpace', (Whitespace,), {}))

    def tearDown(self):
        registry._registry = self._saved
