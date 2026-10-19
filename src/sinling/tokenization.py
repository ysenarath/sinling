"""The ``tokenize`` and ``sentences`` tasks and their rule-based backends.

Ported from 0.3's ``SinhalaTokenizer`` and ``SinhalaTweetTokenizer``. Unlike 0.3, tokenizing
never changes the text (use ``normalize`` first), so every token maps back to the original.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from typing import Any

from sinling.doc import Doc, Span, Token
from sinling.errors import DocError
from sinling.registry import Backend, define_task, get_backend, register, run_task

__all__ = ['ABBREVIATIONS', 'RuleSentenceSplitter', 'RuleTokenizer', 'sentences', 'tokenize', 'tokenized']

# Abbreviations that keep their full stop. Most come from 0.3; the rest are common in Sinhala
# writing: ප.ව. (p.m.), ක්රි.පූ. (BC), අ.පො.ස. (G.C.E.), උ.පෙ. and සා.පෙ. (A/L and O/L).
ABBREVIATIONS = (
    'ඒ.', 'බී.', 'සී.', 'ඩී.', 'ඊ.', 'එෆ්.', 'ජී.', 'එච්.', 'අයි.', 'ජේ.', 'කේ.', 'එල්.', 'එම්.',
    'එන්.', 'ඕ.', 'පී.', 'කිව්.', 'ආර්.', 'එස්.', 'ටී.', 'යූ.', 'වී.', 'ඩබ.', 'ඩබ්ලිව්.', 'ඩබ්.',
    'එක්ස්.', 'වයි.', 'ඉසෙඩ්.', 'පෙ.', 'ව.', 'රු.', 'පා.',
    'ප.', 'ක්\N{ZERO WIDTH JOINER}රි.', 'පූ.', 'අ.', 'පො.', 'ස.', 'උ.', 'සා.',
)

_SINHALA_LETTERS = f'{chr(0x0D81)}-{chr(0x0DF3)}'  # the Sinhala block without the kunddaliya
_COMBINING = f'{chr(0x0300)}-{chr(0x036F)}'
_W = rf'\w{_SINHALA_LETTERS}{_COMBINING}'  # word characters
_ZWJ = '\N{ZERO WIDTH JOINER}'
_JOINERS = '\N{ZERO WIDTH NON-JOINER}' + _ZWJ
_WORD = rf'[{_W}](?:[{_W}]|[{_JOINERS}](?=[{_W}]))*'  # joiners only inside a word
_EMOJI_BASE = r'[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF]'
_EMOJI_MODS = r'[\U0000FE0F\U0001F3FB-\U0001F3FF]*'

_TOKEN_PATTERNS = [
    ('url', r'(?:https?://|www\.)[^\s<>"]+?(?=[.,;:!?)\]}\'"]*(?:\s|$))'),
    ('email', r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+'),
    ('mention', rf'(?<![{_W}])@{_WORD}'),
    ('hashtag', rf'(?<![{_W}])#{_WORD}'),
    ('emoji', rf'[\U0001F1E6-\U0001F1FF]{{2}}|{_EMOJI_BASE}{_EMOJI_MODS}'
              rf'(?:{_ZWJ}{_EMOJI_BASE}{_EMOJI_MODS})*'),
    ('abbreviation', None),  # built per backend from its abbreviation list
    ('number', rf'\d+(?:[.,:/]\d+)*(?![{_W}])'),
    ('word', _WORD),
    ('punct', r'(?P<mark>[^\w\s])(?P=mark)*'),
]

_TERMINATORS = frozenset('.?!\N{HORIZONTAL ELLIPSIS}\N{SINHALA PUNCTUATION KUNDDALIYA}')
_CLOSERS = frozenset('"\')]}\N{RIGHT DOUBLE QUOTATION MARK}\N{RIGHT SINGLE QUOTATION MARK}'
                     '\N{RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK}')
_BULLETS = frozenset(['-', '*', '\N{BULLET}', '\N{WHITE BULLET}', '\N{TRIANGULAR BULLET}', '\N{EN DASH}'])
_BLANK_LINE = re.compile(r'\n[^\S\n]*\n')


def _token_regex(abbreviations: Iterable[str]) -> re.Pattern[str]:
    forms = sorted({unicodedata.normalize('NFC', a) for a in abbreviations}, key=len, reverse=True)
    abbreviation = rf'(?<![{_W}])(?:{"|".join(map(re.escape, forms))})+' if forms else r'(?!x)x'
    parts = [f'(?P<{kind}>{abbreviation if pattern is None else pattern})' for kind, pattern in _TOKEN_PATTERNS]
    return re.compile('|'.join(parts))


def _kind(match: re.Match[str]) -> str:
    kind = match.lastgroup or 'punct'
    if kind == 'punct':
        category = unicodedata.category(match.group()[0])
        kind = 'punct' if category.startswith('P') else 'symbol' if category.startswith('S') else 'other'
    return kind


define_task('tokenize', lambda doc: [t.text for t in doc.tokens],
            description='Split text into words, numbers, punctuation and other tokens.')
define_task('sentences', lambda doc: [doc.span_text(s) for s in doc.sents],
            description='Split tokenized text into sentences.')


@register('tokenize', 'rules', default=True)
class RuleTokenizer(Backend):
    """Regex tokenizer. Sets ``attrs['kind']`` on each token: word, number, punct, symbol,
    abbreviation, url, email, mention, hashtag, emoji or other.

    Pass ``abbreviations=`` to replace the abbreviation list, or ``extra_abbreviations=`` to add
    to it. Runs of the same punctuation mark (``...``, ``!!``) are one token.
    """

    def __init__(self, abbreviations: Iterable[str] = ABBREVIATIONS,
                 extra_abbreviations: Iterable[str] = (), **config: Any) -> None:
        abbreviations, extra_abbreviations = tuple(abbreviations), tuple(extra_abbreviations)
        super().__init__(abbreviations=abbreviations, extra_abbreviations=extra_abbreviations, **config)
        self._regex = _token_regex(abbreviations + extra_abbreviations)

    def __call__(self, doc: Doc) -> Doc:
        doc.set_tokens(Token(m.group(), m.start(), m.end(), {'kind': _kind(m)})
                       for m in self._regex.finditer(doc.text))
        return doc


@register('sentences', 'rules', default=True)
class RuleSentenceSplitter(Backend):
    """Ends a sentence after ``. ? ! …`` or the kunddaliya (``෴``), at blank lines, and before
    a list item.

    Closing quotes and brackets after the full stop stay with the sentence. A list item is a line
    that starts with a number and a full stop (``1.``) or a bullet; that full stop is not a
    sentence end.
    """

    def __call__(self, doc: Doc) -> Doc:
        if not doc.is_tokenized:
            raise DocError("sentences needs tokens; run 'tokenize' first")
        tokens, text = doc.tokens, doc.text

        def is_terminator(token: Token) -> bool:
            return token.attrs.get('kind') == 'punct' and set(token.text) <= _TERMINATORS

        def starts_line(i: int) -> bool:
            return i == 0 or '\n' in text[tokens[i - 1].end:tokens[i].start]

        def is_list_item(i: int) -> bool:
            if not starts_line(i):
                return False
            if tokens[i].text in _BULLETS:
                return True
            return (tokens[i].attrs.get('kind') == 'number' and i + 1 < len(tokens)
                    and tokens[i + 1].text == '.' and tokens[i + 1].start == tokens[i].end)

        sents, start, i = [], 0, 0
        while i < len(tokens):
            token, end = tokens[i], None
            if is_terminator(token) and not (i > 0 and token.text == '.' and is_list_item(i - 1)):
                # keep following terminators (?!) and closing quotes or brackets that touch it
                end = i + 1
                while (end < len(tokens) and tokens[end].start == tokens[end - 1].end
                       and (tokens[end].text in _CLOSERS or is_terminator(tokens[end]))):
                    end += 1
            elif i + 1 < len(tokens) and (
                    _BLANK_LINE.search(text, token.end, tokens[i + 1].start) or is_list_item(i + 1)):
                end = i + 1
            if end is None:
                i += 1
                continue
            sents.append(Span(start, end))
            start = i = end
        if start < len(tokens):
            sents.append(Span(start, len(tokens)))
        doc.sents = sents
        return doc


def _prepare(text: str | Doc, normalize: bool) -> Doc:
    if isinstance(text, Doc):
        return text
    doc = Doc(text)
    return get_backend('normalize')(doc) if normalize else doc


def tokenize(text: str | Doc, *, backend: str | None = None, normalize: bool = True, **config: Any) -> list[str]:
    """Split text into tokens. A string is normalized first unless ``normalize=False``."""
    return run_task('tokenize', _prepare(text, normalize), backend, **config)


def tokenized(text: str | Doc, normalize: bool = True) -> Doc:
    """Return ``text`` as a tokenized Doc, normalizing and tokenizing with the default backends."""
    doc = _prepare(text, normalize)
    if not doc.is_tokenized:
        get_backend('tokenize')(doc)
    return doc


def sentences(text: str | Doc, *, backend: str | None = None, normalize: bool = True, **config: Any) -> list[str]:
    """Split text into sentences, tokenizing it first if needed."""
    return run_task('sentences', tokenized(text, normalize), backend, **config)
