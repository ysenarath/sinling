# Words and sentences

## Splitting into words

`tokenize()` splits text into words, numbers, punctuation marks and other pieces, called
tokens. The text is cleaned up with `normalize()` first. Tokens are always exact pieces of the
text, so you can find each one in the original.

```python
>>> import sinling
>>> sinling.tokenize("ඔහු (COVID-19) ගැන 3.14% ක් කීවේය!")
['ඔහු', '(', 'COVID', '-', '19', ')', 'ගැන', '3.14', '%', 'ක්', 'කීවේය', '!']

```

In a pipeline, each token also says what kind of token it is, in `token.attrs["kind"]`:

| Kind | Examples |
| --- | --- |
| `word` | `ගෙදර`, `COVID`, `10ට` (a number with a suffix counts as a word) |
| `number` | `2026`, `3.14`, `1,000`, `10:30` |
| `abbreviation` | `පෙ.ව.`, `රු.`, `ඒ.බී.` |
| `punct` | `.`, `,`, `...` (repeated marks stay together) |
| `symbol` | `%`, `£`, `©` |
| `url`, `email`, `mention`, `hashtag` | `https://example.lk`, `name@example.lk`, `@user`, `#ශ්‍රීලංකාව` |
| `emoji` | an emoji, including skin tones and combined emoji |
| `other` | anything else |

```python
>>> doc = sinling.pipeline(["tokenize"])("රු.500 #ශ්\N{ZERO WIDTH JOINER}රීලංකා")
>>> [(t.text, t.attrs["kind"]) for t in doc.tokens][:3]
[('රු.', 'abbreviation'), ('500', 'number'), ('#ශ්\u200dරීලංකා', 'hashtag')]

```

### Abbreviations

Common abbreviations such as `රු.` and `පෙ.ව.` keep their full stop. A word only counts as an
abbreviation at its start, so a sentence ending in `ගව.` still ends there.

Some abbreviations are also everyday words, like `ඒ` ("that"). These keep the full stop only
when another abbreviation follows straight after, as in `ඒ.බී.` or `පා.ම.`; otherwise `ඒ.` is the
word `ඒ` and a full stop.

To add your own abbreviations, pass `extra_abbreviations=`:

```python
>>> sinling.tokenize("ඩො. සිල්වා", extra_abbreviations=["ඩො."])
['ඩො.', 'සිල්වා']

```

The full lists are `sinling.tokenization.ABBREVIATIONS` and `CHAIN_ABBREVIATIONS`; you can
replace them with `abbreviations=` and `chain_abbreviations=`.

## Splitting into sentences

`sentences()` splits text into sentences. A sentence ends:

- after `.` `?` `!` `…` or the kunddaliya `෴`, together with any closing quote or bracket right
  after it;
- at a blank line;
- before a new list item, a line that starts with a number and a full stop (`1.`) or a bullet.

```python
>>> sinling.sentences('ඔහු කීවේ "මම එනවා." ඊට පසු ගියේය.')
['ඔහු කීවේ "මම එනවා."', 'ඊට පසු ගියේය.']

>>> sinling.sentences("1. පළමු කරුණ\n2. දෙවන කරුණ")
['1. පළමු කරුණ', '2. දෙවන කරුණ']

```

An abbreviation doesn't end a sentence, and neither does a colon or semicolon.

In a pipeline, the sentences are in `doc.sents`:

```python
>>> doc = sinling.pipeline()("මම යනවා. ඔයා එනවා.")
>>> [doc.span_text(s) for s in doc.sents]
['මම යනවා.', 'ඔයා එනවා.']

```
