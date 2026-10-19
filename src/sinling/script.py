"""Sinhala script: character classes, vowel tables and akshara segmentation.

Ported from 0.3's ``sinling/sinhala/letters.py`` and extended. Character names follow the
Unicode Standard (Sinhala block, U+0D80–U+0DFF).
"""

from __future__ import annotations

import re

__all__ = [
    'AL_LAKUNA', 'ANUSVARA', 'CONSONANTS', 'INDEPENDENT_VOWELS', 'KOMBUVA', 'VISARGA',
    'VOWEL_SIGNS', 'VOWEL_TO_SIGN', 'ZWJ', 'ZWNJ', 'aksharas', 'is_sinhala',
]

ZWJ = '\u200d'
ZWNJ = '\u200c'
AL_LAKUNA = '\u0dca'  # virama: ක + ් = ක්
KOMBUVA = '\u0dd9'  # ෙ, the vowel sign written before its consonant
ANUSVARA = '\u0d82'  # ං
VISARGA = '\u0d83'  # ඃ

INDEPENDENT_VOWELS = 'අආඇඈඉඊඋඌඍඎඏඐඑඒඓඔඕඖ'
CONSONANTS = 'කඛගඝඞඟචඡජඣඤඥඦටඨඩඪණඬතථදධනඳපඵබභමඹයරලවශෂසහළෆ'
VOWEL_SIGNS = '\u0dcf\u0dd0\u0dd1\u0dd2\u0dd3\u0dd4\u0dd6\u0dd8\u0dd9\u0dda\u0ddb\u0ddc\u0ddd\u0dde\u0ddf\u0df2\u0df3'
SIGNS = AL_LAKUNA + VOWEL_SIGNS  # everything that attaches to a consonant
MODIFIERS = '\u0d81' + ANUSVARA + VISARGA  # candrabindu, anusvara, visarga

# Independent vowel -> the vowel sign that gives a consonant the same vowel (අ has none).
VOWEL_TO_SIGN = {
    'අ': '', 'ආ': '\u0dcf', 'ඇ': '\u0dd0', 'ඈ': '\u0dd1', 'ඉ': '\u0dd2', 'ඊ': '\u0dd3', 'උ': '\u0dd4', 'ඌ': '\u0dd6',
    'ඍ': '\u0dd8', 'ඎ': '\u0df2', 'ඏ': '\u0ddf', 'ඐ': '\u0df3', 'එ': '\u0dd9', 'ඒ': '\u0dda', 'ඓ': '\u0ddb', 'ඔ': '\u0ddc',
    'ඕ': '\u0ddd', 'ඖ': '\u0dde',
}

_C = f'[{CONSONANTS}]'
_AKSHARA = re.compile(
    # a consonant, joined to more consonants by ZWJ conjuncts (yansaya, rakaransaya,
    # repaya: ් + ZWJ; touching letters: ZWJ + ්), then its signs and modifiers
    f'{_C}(?:{AL_LAKUNA}{ZWJ}{_C}|{ZWJ}{AL_LAKUNA}{_C})*[{SIGNS}]*[{MODIFIERS}]*'
    # an independent vowel and its modifiers
    f'|[{INDEPENDENT_VOWELS}][{VOWEL_SIGNS}]*[{MODIFIERS}]*'
    # anything else: one character with the combining marks and joiners that follow it
    r'|(?s:.)[\u200c\u200d\u0300-\u036f\u0dca\u0dcf-\u0ddf\u0df2\u0df3\ufe00-\ufe0f]*'
)


def is_sinhala(char: str) -> bool:
    """Whether ``char`` is in the Sinhala block (U+0D80–U+0DFF)."""
    return '\u0d80' <= char <= '\u0dff'


def aksharas(text: str) -> list[str]:
    """Split text into aksharas (written syllables), keeping every character.

    ``''.join(aksharas(text)) == text`` always holds. Non-Sinhala characters come out one
    at a time, each with any combining marks that follow it.

    >>> aksharas('ශ්\u200dරී ලංකාව')
    ['ශ්\u200dරී', ' ', 'ලං', 'කා', 'ව']
    """
    return _AKSHARA.findall(text)
