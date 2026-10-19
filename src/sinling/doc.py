"""The document object shared by all Sinling components."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from sinling.errors import DocError

__all__ = ['Doc', 'Token', 'Span']


@dataclass(slots=True)
class Token:
    """A token, with character offsets into ``Doc.text``."""

    text: str
    start: int
    end: int
    attrs: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Span:
    """A run of tokens ``doc.tokens[start:end]``, with an optional label and score."""

    start: int
    end: int
    label: str | None = None
    score: float | None = None


class Doc:
    """A text and everything Sinling components have found in it.

    ``raw`` is the text exactly as given and never changes. ``text`` is the working text:
    components that run before tokenization (e.g. normalization) may change it through
    `edit_text()`, which keeps an alignment so that any offset in ``text`` can be
    mapped back to ``raw`` with `to_raw()`.
    """

    def __init__(self, raw: str) -> None:
        if not isinstance(raw, str):
            raise TypeError(f'Doc expects a str, got {type(raw).__name__}')
        self.raw = raw
        self._text = raw
        self.tokens: list[Token] = []
        self.sents: list[Span] = []
        self.spans: dict[str, list[Span]] = {}
        self.meta: dict[str, Any] = {}
        self._tokenized = False
        # Alignment from boundaries in ``text`` to boundaries in ``raw``, or None while
        # the text is unchanged. A boundary maps to a different raw offset depending on
        # whether a span starts there (``_starts``) or ends there (``_ends``); the two
        # differ only where characters were deleted.
        self._starts: list[int] | None = None
        self._ends: list[int] | None = None

    @property
    def text(self) -> str:
        return self._text

    @property
    def is_tokenized(self) -> bool:
        return self._tokenized

    def edit_text(self, edits: Iterable[tuple[int, int, str]]) -> None:
        """Replace ``text[start:end]`` with a new string for each ``(start, end, replacement)``.

        Offsets refer to the current ``text``. Edits must not overlap; an empty range inserts
        and an empty replacement deletes. Each character of a replacement maps back to the
        whole range it replaced.
        """
        if self._tokenized:
            raise DocError(
                'the text cannot change after tokenization; '
                'run text-changing components before tokenize')
        edits = sorted(edits, key=lambda e: (e[0], e[1]))
        if not edits:
            return
        old = self._text
        pieces: list[str] = []
        sources: list[tuple[int, int]] = []  # (start, end) in ``old`` for each new character
        pos = 0
        for start, end, replacement in edits:
            if not 0 <= start <= end <= len(old):
                raise DocError(f'edit ({start}, {end}) is outside the text (length {len(old)})')
            if start < pos:
                raise DocError(f'edit ({start}, {end}) overlaps the previous edit')
            pieces.append(old[pos:start])
            sources.extend((i, i + 1) for i in range(pos, start))
            pieces.append(replacement)
            sources.extend((start, end) for _ in replacement)
            pos = end
        pieces.append(old[pos:])
        sources.extend((i, i + 1) for i in range(pos, len(old)))
        starts = [s for s, _ in sources] + [len(old)]
        ends = [0] + [e for _, e in sources]
        if self._starts is not None and self._ends is not None:
            old_starts, old_ends = self._starts, self._ends
            starts = [old_starts[b] for b in starts]
            ends = [old_ends[b] for b in ends]
        self._text = ''.join(pieces)
        self._starts, self._ends = starts, ends

    def to_raw(self, item: int | Token | Span, end: int | None = None) -> tuple[int, int]:
        """Map a character range in ``text``, a token or a span to ``(start, end)`` in ``raw``."""
        if isinstance(item, Token):
            start, end = item.start, item.end
        elif isinstance(item, Span):
            start, end = self._char_range(item)
        else:
            start = item
            if end is None:
                raise TypeError('to_raw(start, end) needs an end offset')
        if not 0 <= start <= end <= len(self._text):
            raise DocError(f'range ({start}, {end}) is outside the text (length {len(self._text)})')
        if self._starts is None or self._ends is None:
            return start, end
        raw_start, raw_end = self._starts[start], self._ends[end]
        return raw_start, max(raw_start, raw_end)

    def set_tokens(self, tokens: Iterable[Token]) -> None:
        """Set the tokens, checking that they match the text and don't overlap."""
        tokens = list(tokens)
        pos = 0
        for i, token in enumerate(tokens):
            if not pos <= token.start <= token.end <= len(self._text):
                raise DocError(f'token {i} ({token.start}, {token.end}) is out of order or outside the text')
            if self._text[token.start:token.end] != token.text:
                raise DocError(f'token {i} text {token.text!r} does not match the text at its offsets')
            pos = token.end
        self.tokens = tokens
        self._tokenized = True

    def span_text(self, span: Span) -> str:
        start, end = self._char_range(span)
        return self._text[start:end]

    def _char_range(self, span: Span) -> tuple[int, int]:
        if not 0 <= span.start <= span.end <= len(self.tokens):
            raise DocError(f'span ({span.start}, {span.end}) is outside the tokens')
        if span.start == span.end:
            offset = self.tokens[span.start].start if span.start < len(self.tokens) else len(self._text)
            return offset, offset
        return self.tokens[span.start].start, self.tokens[span.end - 1].end

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation; `from_dict()` reverses it."""
        data: dict[str, Any] = {'raw': self.raw, 'text': self._text}
        if self._starts is not None:
            data['alignment'] = {'starts': self._starts, 'ends': self._ends}
        if self._tokenized:
            data['tokens'] = [
                {'text': t.text, 'start': t.start, 'end': t.end, 'attrs': t.attrs} for t in self.tokens]
        if self.sents:
            data['sents'] = [_span_to_dict(s) for s in self.sents]
        if self.spans:
            data['spans'] = {name: [_span_to_dict(s) for s in group] for name, group in self.spans.items()}
        if self.meta:
            data['meta'] = self.meta
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Doc:
        doc = cls(data['raw'])
        doc._text = data.get('text', doc.raw)
        alignment = data.get('alignment')
        if alignment is not None:
            doc._starts, doc._ends = list(alignment['starts']), list(alignment['ends'])
            if not len(doc._starts) == len(doc._ends) == len(doc._text) + 1:
                raise DocError('alignment does not match the text length')
        elif doc._text != doc.raw:
            raise DocError('text differs from raw but no alignment was given')
        if 'tokens' in data:
            doc.set_tokens(Token(t['text'], t['start'], t['end'], dict(t.get('attrs', {}))) for t in data['tokens'])
        doc.sents = [Span(**s) for s in data.get('sents', [])]
        doc.spans = {name: [Span(**s) for s in group] for name, group in data.get('spans', {}).items()}
        doc.meta = dict(data.get('meta', {}))
        return doc

    def __repr__(self) -> str:
        text = self._text if len(self._text) <= 40 else self._text[:37] + '...'
        return f'Doc({text!r}, tokens={len(self.tokens)})'


def _span_to_dict(span: Span) -> dict[str, Any]:
    data: dict[str, Any] = {'start': span.start, 'end': span.end}
    if span.label is not None:
        data['label'] = span.label
    if span.score is not None:
        data['score'] = span.score
    return data
