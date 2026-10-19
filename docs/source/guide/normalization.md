# Normalization

The same Sinhala word can be stored in many ways: typed in visual order, copied from a PDF,
pasted with invisible characters, or with a joiner in the wrong place. They look identical but
don't compare equal, which breaks search, counting and every later step. `normalize()` converts
text to one canonical Unicode form.

```python
>>> import sinling
>>> sinling.normalize("\N{ZERO WIDTH SPACE}\N{SINHALA VOWEL SIGN KOMBUVA}කා\N{NO-BREAK SPACE}අා")
'කො ආ'

```

`tokenize()`, `sentences()`, `stem()` and `from_legacy_font()` normalize their input first,
unless you pass `normalize=False`.

## Rules

The rules run in this order:

| # | Option | What it does | Example |
| --- | --- | --- | --- |
| 1 | `invisible` | Removes zero-width spaces, byte order marks, soft hyphens, word joiners and direction marks. | `ක` U+200B `ර` → `කර` |
| 2 | `zwj` | Puts each zero-width joiner (ZWJ) where SLS 1134 expects it and drops stray ZWJ and ZWNJ. Only joiners next to Sinhala letters are touched, so emoji sequences survive. | `ක` U+200D U+0DCA `ය` → `ක` U+0DCA U+200D `ය` |
| 3 | `doubled_signs` | Two kombuvas become kombu deka (`ෛ`); likewise `ෲ` and `ෳ`. | U+0DD9 U+0DD9 → U+0DDB |
| 4 | `reorder` | Moves a vowel sign typed before its consonant (visual order) after the whole consonant cluster. | U+0DD9 `ග` → `ගෙ` |
| 5 | `vowel_letters` | Replaces an independent vowel plus a sign with the vowel letter, using the Unicode Standard's list of sequences not to use (DoNotEmit.txt). | `අ` + `ා` → `ආ` |
| 6 | `nfc` | Unicode NFC, which merges two-part vowel signs typed in logical order. | U+0DD9 U+0DCF → `ො` |
| 7 | `whitespace` | Turns runs of spaces, tabs and other Unicode spaces into one space, removes spaces around line breaks and trims both ends. Line breaks are kept. | U+00A0 → space |

Joiners are handled before the vowel-sign rules because a stray joiner can hide a sign from
them. Well-formed text needs one pass; on malformed input one rule can enable another, so the
rules repeat (at most four passes) until the text stops changing. Running `normalize()` twice
always gives the same result as running it once.

The SLS 1134 joiner positions are: after the al-lakuna for yansaya (`ක්‍ය`), rakaransaya
(`ක්‍ර`) and repaya (`ර්‍ක`), and before it for touching letters (`ක‍්ව`).

## Presets and options

`preset="standard"` (the default) is safe for display and storage. `preset="search"` also
strips every joiner next to Sinhala letters, so spelling variants match:

```python
>>> sinling.normalize("ශ්\N{ZERO WIDTH JOINER}රී", preset="search") == "ශ්රී"
True

```

Turn single rules off by name. `zwj` takes `"canonical"`, `"strip"` or `"keep"`, and
`whitespace` takes `"collapse"` or `"keep"`:

```python
>>> sinling.normalize("  ගම  ", whitespace="keep")
'  ගම  '

```

## What normalization does not do

- It doesn't convert legacy-font text; use [`from_legacy_font()`](legacy-fonts.md) first.
- It doesn't fold long and short vowels or spelling variants, because that changes meaning.
- Tamil script gets only the NFC and whitespace rules for now.

## Aksharas

`aksharas()` splits text into aksharas, the written syllables of Sinhala. It never loses a
character: joining the result gives back the input.

```python
>>> print(" / ".join(sinling.aksharas("ශ්\N{ZERO WIDTH JOINER}රී ලංකාව")))
ශ්‍රී /   / ලං / කා / ව

```

A consonant joined by a ZWJ conjunct (yansaya, rakaransaya, repaya or touching letters) stays
in one akshara with the next consonant; an explicit al-lakuna (`ස්ත`) ends the akshara.
Characters from other scripts come out one at a time, each with the combining marks that
follow it.
