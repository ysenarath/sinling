# Normalization

The same Sinhala word can be stored in different ways. It might be typed with a vowel sign in
the wrong order, copied from a PDF, or pasted with invisible characters inside. On screen the
words look the same, but a computer treats them as different words, so search and word counts
go wrong. `normalize()` cleans up the text so that the same word is always stored the same way.

```python
>>> import sinling
>>> sinling.normalize("\N{ZERO WIDTH SPACE}\N{SINHALA VOWEL SIGN KOMBUVA}කා\N{NO-BREAK SPACE}අා")
'කො ආ'

```

`tokenize()`, `sentences()`, `stem()` and `from_legacy_font()` clean up your text this way
first. Pass `normalize=False` if you don't want that.

## What it fixes

| Option | What it fixes | Example |
| --- | --- | --- |
| `invisible` | Removes invisible characters: zero-width spaces, byte order marks, soft hyphens and direction marks. | `ක` + zero-width space + `ර` → `කර` |
| `zwj` | Puts the zero-width joiner (ZWJ) used in `ක්‍ය`, `ක්‍ර`, `ර්‍ක` and `ක‍්ව` where the Sinhala Unicode standard (SLS 1134) expects it, and removes joiners that don't belong. Joiners in emoji are left alone. | `ක` + ZWJ + `්` + `ය` → `ක්‍ය` |
| `doubled_signs` | Two kombuvas typed for kombu deka become `ෛ`; the same for `ෲ` and `ෳ`. | `ම` + `ෙ` + `ෙ` → `මෛ` |
| `reorder` | Moves a kombuva typed before its letter, as on an old typewriter, to after it. | `ෙ` + `ග` → `ගෙ` |
| `vowel_letters` | Replaces a vowel letter plus a sign with the single vowel letter. | `අ` + `ා` → `ආ` |
| `nfc` | Joins vowel signs typed in two parts. | `ක` + `ෙ` + `ා` → `කො` |
| `whitespace` | Turns runs of spaces and tabs into one space and trims the ends of each line. Line breaks are kept. | no-break space → space |

Running `normalize()` on text that is already clean doesn't change it.

## Options

The default is safe for showing and storing text. For search, use `preset="search"`, which
also removes the joiners, so `ශ්‍රී` and `ශ්රී` match:

```python
>>> sinling.normalize("ශ්\N{ZERO WIDTH JOINER}රී", preset="search") == "ශ්රී"
True

```

Turn off any fix by its option name. `zwj` can also be `"strip"` (remove all joiners) or
`"keep"`, and `whitespace` can be `"keep"`:

```python
>>> sinling.normalize("  ගම  ", whitespace="keep")
'  ගම  '

```

## What it doesn't do

- It doesn't convert text typed in old fonts; use [`from_legacy_font()`](legacy-fonts.md) for that.
- It doesn't change spellings or long and short vowels, because that can change the meaning.
- For Tamil text it only joins vowel signs and tidies spaces.

## Aksharas

`aksharas()` splits text into aksharas, the written syllables of Sinhala. Nothing is lost:
joining the pieces gives back the original text.

```python
>>> print(" / ".join(sinling.aksharas("ශ්\N{ZERO WIDTH JOINER}රී ලංකාව")))
ශ්‍රී /   / ලං / කා / ව

```

Letters joined with a ZWJ, as in `ශ්‍රී` or `ක්‍ය`, stay in one akshara. A letter with a visible
al-lakuna, as in `ස්ත`, is an akshara of its own. Letters from other scripts come out one at a
time.
