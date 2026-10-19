# Tokens and sentences

## Tokenization

`tokenize()` splits text into words, numbers, punctuation and other tokens. A string is
normalized first; tokenizing itself never changes the text, so every token maps back to the
original.

```python
>>> import sinling
>>> sinling.tokenize("ඔහු (COVID-19) ගැන 3.14% ක් කීවේය!")
['ඔහු', '(', 'COVID', '-', '19', ')', 'ගැන', '3.14', '%', 'ක්', 'කීවේය', '!']

```

In a pipeline, each token records its kind in `token.attrs["kind"]`:

| Kind | Examples |
| --- | --- |
| `word` | `ගෙදර`, `COVID`, `10ට` (a number with a suffix is one word) |
| `number` | `2026`, `3.14`, `1,000`, `10:30` |
| `abbreviation` | `පෙ.ව.`, `රු.`, `ඒ.බී.` |
| `punct` | `.`, `,`, `...` (a run of the same mark is one token) |
| `symbol` | `%`, `£`, `©` |
| `url`, `email`, `mention`, `hashtag` | `https://example.lk`, `name@example.lk`, `@user`, `#ශ්‍රීලංකාව` |
| `emoji` | an emoji with its skin tone or ZWJ sequence |
| `other` | anything else, such as a stray combining mark |

```python
>>> doc = sinling.pipeline(["tokenize"])("රු.500 #ශ්\N{ZERO WIDTH JOINER}රීලංකා")
>>> [(t.text, t.attrs["kind"]) for t in doc.tokens][:3]
[('රු.', 'abbreviation'), ('500', 'number'), ('#ශ්\u200dරීලංකා', 'hashtag')]

```

### Abbreviations

Known abbreviations keep their full stop. They are recognized only at the start of a word, so
a sentence ending in `ගව.` still ends there. There are two lists:

- `ABBREVIATIONS` stand alone: initials such as `බී.` and `එම්.`, and `රු.`, `ක්‍රි.`.
- `CHAIN_ABBREVIATIONS` are also common words (`ඒ` "that", `පා`) or occur only in chains such as
  `පෙ.ව.`, `අ.පො.ස.` and `පා.ම.`. They keep their full stop only when another abbreviation
  follows directly.

Add your own with `extra_abbreviations=`, or replace either list with `abbreviations=` or
`chain_abbreviations=`:

```python
>>> sinling.tokenize("ඩො. සිල්වා", extra_abbreviations=["ඩො."])
['ඩො.', 'සිල්වා']

```

## Sentences

`sentences()` splits text into sentences, tokenizing it first if needed. A sentence ends:

- after `.` `?` `!` `…` or the kunddaliya `෴`, together with any closing quotes or brackets that
  touch it;
- at a blank line;
- before a list item: a line starting with a number and a full stop (`1.`) or a bullet.

```python
>>> sinling.sentences('ඔහු කීවේ "මම එනවා." ඊට පසු ගියේය.')
['ඔහු කීවේ "මම එනවා."', 'ඊට පසු ගියේය.']

>>> sinling.sentences("1. පළමු කරුණ\n2. දෙවන කරුණ")
['1. පළමු කරුණ', '2. දෙවන කරුණ']

```

Abbreviations don't end a sentence, and a number followed by a full stop at the start of a line
is a list marker. A colon or semicolon never ends a sentence.

In a pipeline, the sentences are stored as `doc.sents`, spans of token indices:

```python
>>> doc = sinling.pipeline()("මම යනවා. ඔයා එනවා.")
>>> [doc.span_text(s) for s in doc.sents]
['මම යනවා.', 'ඔයා එනවා.']

```
