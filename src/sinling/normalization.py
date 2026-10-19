"""The ``normalize`` task: one canonical Unicode form for Sinhala text.

Rules run in this order, each recording an alignment back to the input:

1. ``invisible``: remove zero-width spaces, BOMs, soft hyphens, word joiners and direction marks.
2. ``doubled_signs``: compose a doubled vowel sign into its single character (\u0dd9 + \u0dd9 -> \u0ddb).
3. ``reorder``: move a vowel sign typed before its consonant (visual order) after it.
4. ``vowel_letters``: replace an independent vowel + sign with the precomposed vowel letter
   (අ + \u0dcf -> ආ), following the Unicode Standard's DoNotEmit.txt.
5. ``zwj``: ``'canonical'`` puts each ZWJ in its SLS 1134 position and drops stray ZWJ and
   ZWNJ; ``'strip'`` removes them all; ``'keep'`` leaves them. Only joiners next to a Sinhala
   character are touched, so emoji sequences survive.
6. ``nfc``: Unicode NFC, which merges two-part vowel signs typed in logical order.
7. ``whitespace``: ``'collapse'`` turns runs of spaces, tabs and other Unicode spaces into one
   space, removes spaces around line breaks and trims both ends; ``'keep'`` leaves them.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable
from typing import Any

from sinling.doc import Doc
from sinling.registry import Backend, define_task, register, run_task
from sinling.script import AL_LAKUNA, CONSONANTS, INDEPENDENT_VOWELS, KOMBUVA, ZWJ, ZWNJ

__all__ = ['PRESETS', 'RuleNormalizer', 'normalize']

Edits = list[tuple[int, int, str]]

PRESETS: dict[str, dict[str, Any]] = {
    'standard': {
        'invisible': True, 'doubled_signs': True, 'reorder': True, 'vowel_letters': True,
        'zwj': 'canonical', 'nfc': True, 'whitespace': 'collapse',
    },
}
PRESETS['search'] = {**PRESETS['standard'], 'zwj': 'strip'}

_CHOICES = {'zwj': ('canonical', 'strip', 'keep'), 'whitespace': ('collapse', 'keep')}

_INVISIBLE = re.compile('[\u00ad\u061c\u200b\u200e\u200f\u202a-\u202e\u2060\u2066-\u2069\ufeff]+')

# Doubled signs typed for one sign. Not in Unicode's DoNotEmit list; reviewed by the maintainer (2026-10-18).
_DOUBLED = {
    '\u0dd9\u0dd9': '\u0ddb',  # ෙ + ෙ -> ෛ (kombu deka)
    '\u0dd8\u0dd8': '\u0df2',  # ෘ + ෘ -> ෲ (diga gaetta-pilla)
    '\u0ddf\u0ddf': '\u0df3',  # ෟ + ෟ -> ෳ (diga gayanukitta)
}

# From DoNotEmit.txt (Unicode 18.0), type Indic_Vowel_Letter, based on Table 13-2.
_VOWEL_LETTERS = {
    'අා': 'ආ',  # අ + ා -> ආ
    'අැ': 'ඇ',  # අ + ැ -> ඇ
    'අෑ': 'ඈ',  # අ + ෑ -> ඈ
    'උෟ': 'ඌ',  # උ + ෟ -> ඌ
    'ඍෘ': 'ඎ',  # ඍ + ෘ -> ඎ
    'ඏෟ': 'ඐ',  # ඏ + ෟ -> ඐ
    'එ්': 'ඒ',  # එ + ් -> ඒ
    'එෙ': 'ඓ',  # එ + ෙ -> ඓ
    'ඔෟ': 'ඖ',  # ඔ + ෟ -> ඖ
}

_PRE_BASE = KOMBUVA + '\u0dda\u0ddb'  # ෙ ේ ෛ are written before their consonant
_CONSONANT = frozenset(CONSONANTS)
_C = f'[{CONSONANTS}]'
_CLUSTER = re.compile(f'{_C}(?:{AL_LAKUNA}{ZWJ}{_C}|{ZWJ}{AL_LAKUNA}{_C})*')
_EYANNA = re.compile('එ')  # ෙ typed before එ is the visual order of ඓ
_SINHALA = '\u0d80-\u0dff'
# A run of joiners with a Sinhala character on at least one side.
_JOINERS = re.compile(f'(?<=[{_SINHALA}])[{ZWJ}{ZWNJ}]+|[{ZWJ}{ZWNJ}]+(?=[{_SINHALA}])')
# ZWJ before al-lakuna where SLS 1134 puts it after: yansaya, rakaransaya and repaya.
_ZWJ_MISPLACED = re.compile(f'(?<={_C}){ZWJ}{AL_LAKUNA}(?=[යර])|(?<=ර){ZWJ}{AL_LAKUNA}(?={_C})')
_MAX_PASSES = 4
# Characters NFC never composes with what comes before: a safe place to cut the text.
_NFC_SAFE = set(CONSONANTS + INDEPENDENT_VOWELS)
_SPACES = re.compile('[ \t\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000]+')
_SPACE_AT_BREAK = re.compile('(?<=[\r\n]) | (?=[\r\n])')


def _remove_invisible(text: str, opts: dict[str, Any]) -> Edits:
    return [(m.start(), m.end(), '') for m in _INVISIBLE.finditer(text)]


def _replace_table(table: dict[str, str]) -> Callable[[str, dict[str, Any]], Edits]:
    pattern = re.compile('|'.join(map(re.escape, table)))

    def rule(text: str, opts: dict[str, Any]) -> Edits:
        return [(m.start(), m.end(), table[m.group()]) for m in pattern.finditer(text)]

    return rule


def _reorder(text: str, opts: dict[str, Any]) -> Edits:
    edits, i, moved = [], 0, False
    while i < len(text) - 1:
        sign = text[i]
        # A sign right after a consonant is in logical order, unless that consonant
        # already took a sign that was just moved after it.
        if sign in _PRE_BASE and (moved or i == 0 or text[i - 1] not in _CONSONANT):
            cluster = _CLUSTER.match(text, i + 1)
            if cluster is None and sign == KOMBUVA:
                cluster = _EYANNA.match(text, i + 1)
            if cluster is not None:
                edits.append((i, cluster.end(), cluster.group() + sign))
                i, moved = cluster.end(), True
                continue
        i, moved = i + 1, False
    return edits


def _joiners(text: str, opts: dict[str, Any]) -> Edits:
    edits = []
    for m in _JOINERS.finditer(text):
        keep = ''
        if opts['zwj'] == 'canonical' and ZWJ in m.group():
            before, after = text[m.start() - 1:m.start()], text[m.end():m.end() + 1]
            # One ZWJ stays in ් + ZWJ + consonant (yansaya, rakaransaya, repaya)
            # and in consonant + ZWJ + ් (touching letters).
            if (before == AL_LAKUNA and after in _CONSONANT) or (before in _CONSONANT and after == AL_LAKUNA):
                keep = ZWJ
        if m.group() != keep:
            edits.append((m.start(), m.end(), keep))
    return edits


def _zwj_order(text: str, opts: dict[str, Any]) -> Edits:
    if opts['zwj'] != 'canonical':
        return []
    return [(m.start(), m.end(), AL_LAKUNA + ZWJ) for m in _ZWJ_MISPLACED.finditer(text)]


def _nfc(text: str, opts: dict[str, Any]) -> Edits:
    if unicodedata.is_normalized('NFC', text):
        return []
    edits, start = [], 0
    for i in range(1, len(text) + 1):
        if i == len(text) or text[i] < '\u0300' or text[i] in _NFC_SAFE:
            chunk = text[start:i]
            normalized = unicodedata.normalize('NFC', chunk)
            if normalized != chunk:
                edits.append((start, i, normalized))
            start = i
    return edits


def _collapse_spaces(text: str, opts: dict[str, Any]) -> Edits:
    return [(m.start(), m.end(), ' ') for m in _SPACES.finditer(text) if m.group() != ' ']


def _trim_lines(text: str, opts: dict[str, Any]) -> Edits:
    start, end = len(text) - len(text.lstrip()), len(text.rstrip())
    if end == 0:
        return [(0, len(text), '')] if text else []
    edits = [(m.start(), m.end(), '') for m in _SPACE_AT_BREAK.finditer(text, start, end)]
    if start:
        edits.append((0, start, ''))
    if end < len(text):
        edits.append((end, len(text), ''))
    return edits


# (option, rule) pairs in the order they run; each runs while its option is truthy.
_RULES: list[tuple[str, Callable[[str, dict[str, Any]], Edits]]] = [
    ('invisible', _remove_invisible),
    ('zwj', _joiners),
    ('zwj', _zwj_order),
    ('doubled_signs', _replace_table(_DOUBLED)),
    ('reorder', _reorder),
    ('vowel_letters', _replace_table(_VOWEL_LETTERS)),
    ('nfc', _nfc),
    ('whitespace', _collapse_spaces),
    ('whitespace', _trim_lines),
]


def _resolve(preset: str, options: dict[str, Any]) -> dict[str, Any]:
    if preset not in PRESETS:
        raise ValueError(f'unknown preset {preset!r}; choose from {", ".join(PRESETS)}')
    unknown = set(options) - set(PRESETS[preset])
    if unknown:
        raise TypeError(f'unknown normalize option(s): {", ".join(sorted(unknown))}; '
                        f'valid: {", ".join(PRESETS[preset])}')
    resolved = {**PRESETS[preset], **options}
    for name, choices in _CHOICES.items():
        if resolved[name] not in choices:
            raise ValueError(f'{name}={resolved[name]!r}; choose from {", ".join(choices)}')
    return resolved


define_task('normalize', lambda doc: doc.text, changes_text=True,
            description='Convert Sinhala text to one canonical Unicode form.')


@register('normalize', 'rules', default=True)
class RuleNormalizer(Backend):
    """Rule-based normalizer. Pure Python; needs no download."""

    def __init__(self, preset: str = 'standard', **options: Any) -> None:
        super().__init__(preset=preset, **options)
        self.options = _resolve(preset, options)

    def __call__(self, doc: Doc) -> Doc:
        rules = [rule for option, rule in _RULES if self.options[option] not in (False, 'keep')]
        for _ in range(_MAX_PASSES):
            changed = False
            for rule in rules:
                edits = rule(doc.text, self.options)
                if edits:
                    doc.edit_text(edits)
                    changed = True
            if not changed:
                break
        return doc


def normalize(text: str | Doc, *, preset: str = 'standard', backend: str | None = None, **options: Any) -> str:
    """Return ``text`` in canonical Unicode form.

    ``preset='standard'`` is safe for display and storage; ``preset='search'`` also strips
    ZWJ so that spelling variants match. Override single rules by name, e.g. ``zwj='keep'``.
    """
    result: str = run_task('normalize', text, backend, preset=preset, **options)
    return result
