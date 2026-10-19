"""The ``legacy_font`` task: convert text typed in legacy Sinhala fonts to Unicode.

Legacy fonts draw Sinhala glyphs on Latin code points, so text extracted from a PDF or Word file
that uses them reads as Latin gibberish ("jd;h" for වාතය). The ``fm`` backend handles the FM
family (FMAbhaya, FMMalithi, FMEmanee, FMAbabld, ...), which shares the Wijesekara layout.

Only convert text that is actually in a legacy font: Latin letters and punctuation are remapped,
so ordinary English text would be garbled. In a PDF, choose spans by font with ``is_fm_font``.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from sinling._fm_tables import CHARS, INDEPENDENT_VOWELS, KOMBUVA, SEQUENCES
from sinling.doc import Doc
from sinling.registry import Backend, define_task, get_backend, register
from sinling.script import AL_LAKUNA, ZWJ, ZWNJ, is_sinhala

__all__ = ['FMConverter', 'from_legacy_font', 'is_fm_font']

# FM-encoded fonts that don't start with "FM", seen in the Educational Publications Department textbooks.
FM_FONTS_WITHOUT_PREFIX = ('SARAWIPULA', 'Chamodi', '0KDBOLIDDAbold')

_K = re.escape(KOMBUVA)
_CONSONANT = '[ක-ෆ]'
_MEDIAL = f'(?:{AL_LAKUNA}{ZWJ}[යර])?'  # yansaya or rakaransaya, typed after the consonant
_VOWEL_SIGN = f'[{chr(0x0DCF)}-{chr(0x0DDF)}{chr(0x0DF2)}{chr(0x0DF3)}]'
_AELA = '\N{SINHALA VOWEL SIGN AELA-PILLA}'
_GAYANUKITTA = '\N{SINHALA VOWEL SIGN GAYANUKITTA}'

# The kombuva comes before its consonant in FM text; these move it after, composing it with the
# signs that follow. Applied in order.
_REORDER = [
    (re.compile(f'{_K}{_K}({_CONSONANT}{_MEDIAL})'), r'\1' + '\N{SINHALA VOWEL SIGN KOMBU DEKA}'),
    (re.compile(f'{_K}({_CONSONANT}{_MEDIAL}){_AELA}{AL_LAKUNA}'),
     r'\1' + '\N{SINHALA VOWEL SIGN KOMBUVA HAA DIGA AELA-PILLA}'),
    (re.compile(f'{_K}({_CONSONANT}{_MEDIAL}){_AELA}'), r'\1' + '\N{SINHALA VOWEL SIGN KOMBUVA HAA AELA-PILLA}'),
    (re.compile(f'{_K}({_CONSONANT}{_MEDIAL}){AL_LAKUNA}'), r'\1' + '\N{SINHALA VOWEL SIGN DIGA KOMBUVA}'),
    (re.compile(f'{_K}({_CONSONANT}{_MEDIAL}){_GAYANUKITTA}'), r'\1' + '\N{SINHALA VOWEL SIGN KOMBUVA HAA GAYANUKITTA}'),
    (re.compile(f'{_K}({_CONSONANT}{_MEDIAL})'), r'\1' + '\N{SINHALA VOWEL SIGN KOMBUVA}'),
    # a vowel sign typed before a yansaya or rakaransaya ("YS%" for ශ්රී)
    (re.compile(f'({_VOWEL_SIGN})({AL_LAKUNA}{ZWJ}[යර])'), r'\2\1'),
]
_SEQUENCE = re.compile('|'.join(re.escape(s) for s in sorted(SEQUENCES, key=len, reverse=True)))
_VOWELS = re.compile('|'.join(INDEPENDENT_VOWELS))
_PASS_THROUGH = '-()_' + ZWNJ + ZWJ  # characters that are the same in FM and Unicode


def is_fm_font(name: str) -> bool:
    """Whether a PDF font name (e.g. ``ABCDEF+FMAbhaya``) is FM-encoded."""
    family = name.split('+', 1)[-1]
    return family.upper().startswith('FM') or family in FM_FONTS_WITHOUT_PREFIX


def _map_characters(text: str) -> tuple[list[tuple[int, int, str]], Counter[str]]:
    edits: list[tuple[int, int, str]] = []
    unmapped: Counter[str] = Counter()
    i = 0
    while i < len(text):
        sequence = _SEQUENCE.match(text, i)
        if sequence:
            edits.append((i, sequence.end(), SEQUENCES[sequence.group()]))
            i = sequence.end()
            continue
        char = text[i]
        if char in CHARS:
            if CHARS[char] != char:
                edits.append((i, i + 1, CHARS[char]))
        elif char < ' ' and char not in '\t\n':
            edits.append((i, i + 1, ''))  # control characters from broken font encodings
        elif not (char.isspace() or char.isdigit() or char in _PASS_THROUGH or is_sinhala(char)):
            unmapped[char] += 1
        i += 1
    return edits, unmapped


define_task('legacy_font', lambda doc: doc.text, changes_text=True,
            description='Convert text typed in a legacy Sinhala font to Unicode.')


@register('legacy_font', 'fm', default=True)
class FMConverter(Backend):
    """Converts FM-font text. Characters it has no mapping for are kept, and counted in
    ``doc.meta['legacy_font_unmapped']`` so coverage gaps can be found.
    """

    def __call__(self, doc: Doc) -> Doc:
        edits, unmapped = _map_characters(doc.text)
        doc.edit_text(edits)
        for pattern, template in _REORDER:
            doc.edit_text([(m.start(), m.end(), m.expand(template)) for m in pattern.finditer(doc.text)])
        doc.edit_text([(m.start(), m.end(), INDEPENDENT_VOWELS[m.group()]) for m in _VOWELS.finditer(doc.text)])
        # a kombuva with no consonant after it
        doc.edit_text([(m.start(), m.end(), '\N{SINHALA VOWEL SIGN KOMBUVA}') for m in re.finditer(_K, doc.text)])
        if unmapped:
            counts = Counter(doc.meta.get('legacy_font_unmapped', {}))
            counts.update(unmapped)
            doc.meta['legacy_font_unmapped'] = dict(counts)
        return doc


def from_legacy_font(text: str | Doc, *, backend: str = 'fm', normalize: bool = True, **options: Any) -> str:
    """Convert text typed in a legacy font to Unicode, then normalize it unless ``normalize=False``.

    The backend is the font family: ``'fm'`` for the FM fonts.
    """
    doc = text if isinstance(text, Doc) else Doc(text)
    get_backend('legacy_font', backend, **options)(doc)
    if normalize:
        get_backend('normalize')(doc)
    return doc.text
