"""The ``stem`` task: suffix-stripping and dictionary stemmers.

Ported from 0.3's ``SinhalaStemmer``. The algorithm and data come from the sinhala-stemmer of
the "Sinhala News Analysis" project (https://github.com/rksk/sinhala-news-analysis). Its
repository has no licence, so Sinling does not redistribute the data: both files are
downloaded from the authors' repository on first use, pinned to a commit and checked
against a SHA-256 checksum.
"""

from __future__ import annotations

import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, ClassVar

from sinling.doc import Doc
from sinling.errors import DocError
from sinling.registry import Backend, define_task, register, run_task
from sinling.resources import Resource, register_resource, resource_path
from sinling.tokenization import tokenized

__all__ = ['DictionaryStemmer', 'SuffixStemmer', 'stem']

_UPSTREAM = ('https://raw.githubusercontent.com/rksk/sinhala-news-analysis/'
             '05e7076caa76bfe490f93d221c4aac88c1d01600/sinhala-stemmer/')
_NOTE = 'From rksk/sinhala-news-analysis (sinhala-stemmer). The repository has no licence.'

SUFFIXES = register_resource(Resource(
    'sinhala-suffixes', '05e7076', _UPSTREAM + 'suffixes_list.txt',
    '4d5adc2001d881e5f2ee408d659bdb82c57a4cb9fd3f28fb9012ec38380c3356', size=6372,
    description='Sinhala suffixes for suffix stripping (439 lines, 436 unique). ' + _NOTE))
STEM_DICTIONARY = register_resource(Resource(
    'sinhala-stem-dictionary', '05e7076', _UPSTREAM + 'stem_dictionary.txt',
    'ca17ca28a6e6699a11663b68fc0ac7c3e2998db93d743da9ee5f3a85e59045d9', size=1334514,
    description='27,197 hand-made word-to-stem pairs; the authors note it is incomplete. ' + _NOTE))

_JOINERS = str.maketrans('', '', '\N{ZERO WIDTH JOINER}\N{ZERO WIDTH NON-JOINER}')


def _key(word: str) -> str:
    """Dictionary key: NFC without joiners (the dictionary has no ZWJ conjuncts)."""
    return unicodedata.normalize('NFC', word).translate(_JOINERS)


@lru_cache(maxsize=None)
def load_suffixes(path: Path) -> frozenset[str]:
    """Read the suffix list. 'utf-8-sig' drops the byte order mark at the start of the file.

    The first entry, 'ක', is left out: in 0.3 the byte order mark was glued to it, so it never
    matched, and stripping it would cut the final consonant off words such as නායක.
    """
    lines = path.read_text(encoding='utf-8-sig').split('\n')
    suffixes = {unicodedata.normalize('NFC', line.strip()) for line in lines}
    return frozenset(suffixes - {'', 'ක'})


@lru_cache(maxsize=None)
def load_stem_dictionary(path: Path) -> dict[str, str]:
    """Read ``word<TAB>stem`` lines into ``{key(word): stem}``. Later duplicates win, as in 0.3."""
    entries = {}
    for line in path.read_text(encoding='utf-8-sig').split('\n'):
        parts = line.strip().split('\t')
        if len(parts) == 2 and all(parts):
            entries[_key(parts[0])] = unicodedata.normalize('NFC', parts[1])
    return entries


define_task('stem', lambda doc: [t.attrs['stem'] for t in doc.tokens],
            description='Reduce each word token to its stem.')


@register('stem', 'suffix', default=True)
class SuffixStemmer(Backend):
    """Strips the longest known suffix, as 0.3 did without its dictionary.

    Only ``word`` tokens are stemmed; other tokens keep their text. Sets ``attrs['stem']`` and
    ``attrs['suffix']`` on every token. A word that is itself a suffix is never emptied.
    """

    resources: ClassVar[tuple[str, ...]] = ('sinhala-suffixes',)

    def __init__(self, **config: Any) -> None:
        super().__init__(**config)
        self._suffixes = load_suffixes(resource_path('sinhala-suffixes'))
        self._longest = max(map(len, self._suffixes))

    def split(self, word: str) -> tuple[str, str]:
        """Return ``(stem, suffix)`` for one word."""
        for n in range(min(self._longest, len(word)), 0, -1):
            if word[-n:] in self._suffixes:
                return (word, '') if n == len(word) else (word[:-n], word[-n:])
        return word, ''

    def __call__(self, doc: Doc) -> Doc:
        if not doc.is_tokenized:
            raise DocError("stem needs tokens; run 'tokenize' first")
        for token in doc.tokens:
            stem, suffix = self.split(token.text) if token.attrs.get('kind') == 'word' else (token.text, '')
            token.attrs['stem'], token.attrs['suffix'] = stem, suffix
        return doc


@register('stem', 'dictionary')
class DictionaryStemmer(SuffixStemmer):
    """Looks words up in the stem dictionary first, then strips suffixes.

    When the dictionary's stem is not a prefix of the word (a spelling normalization, e.g.
    ඉන්දීය -> ඉන්දියාව), the stem is returned with an empty suffix.
    """

    resources = ('sinhala-suffixes', 'sinhala-stem-dictionary')

    def __init__(self, **config: Any) -> None:
        super().__init__(**config)
        self._dictionary = load_stem_dictionary(resource_path('sinhala-stem-dictionary'))

    def split(self, word: str) -> tuple[str, str]:
        stem = self._dictionary.get(_key(word))
        if stem is None:
            return super().split(word)
        # Map the stem back onto the word as written, so joiners in the word are kept.
        plain, i = 0, 0
        while i < len(word) and plain < len(stem):
            if word[i] not in '\N{ZERO WIDTH JOINER}\N{ZERO WIDTH NON-JOINER}':
                plain += 1
            i += 1
        if _key(word[:i]) == stem:
            return word[:i], word[i:]
        return stem, ''


def stem(text: str | Doc, *, backend: str | None = None, normalize: bool = True, **options: Any) -> list[str]:
    """Return the stem of each token, tokenizing (and normalizing) a string first."""
    stems: list[str] = run_task('stem', tokenized(text, normalize), backend, **options)
    return stems
