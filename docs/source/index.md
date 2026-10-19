# Sinling

Sinling is a language processing toolkit for Sinhala (සිංහල). It cleans up Sinhala text,
splits it into tokens and sentences, finds stems, converts legacy-font text to Unicode, and
measures how well each of these works on public test sets.

!!! warning "Sinling 0.4 is a pre-release"
    0.4 is a redesign and is not compatible with 0.3. A plain `pip install sinling` still
    installs 0.3. If your code uses the 0.3 API, pin `sinling<0.4`; the
    [migration guide](migration.md) maps the old API to the new one.

## Installation

```
pip install --pre sinling
```

Sinling 0.4 needs Python 3.11 or newer and has no dependencies.

## Quick start

Each task is one function that takes text and returns plain Python values:

```python
>>> import sinling

>>> sinling.normalize("\N{SINHALA VOWEL SIGN KOMBUVA}ගදර\N{NO-BREAK SPACE}යනවා")
'ගෙදර යනවා'

>>> sinling.tokenize("පෙ.ව. 10ට රු.500ක් ගෙවන්න.")
['පෙ.ව.', '10ට', 'රු.', '500ක්', 'ගෙවන්න', '.']

>>> sinling.sentences("මම ගෙදර යනවා. ඔයා එනවද?")
['මම ගෙදර යනවා.', 'ඔයා එනවද?']

```

For everything at once, a pipeline returns a `Doc` that keeps the tokens, the sentences and an
alignment back to the original text:

```python
>>> doc = sinling.pipeline()("මම ගෙදර යනවා. ඔයා එනවද?")
>>> [token.text for token in doc.tokens]
['මම', 'ගෙදර', 'යනවා', '.', 'ඔයා', 'එනවද', '?']
>>> len(doc.sents)
2

```

## What's included

| Task | Function | Backends | Downloads |
| --- | --- | --- | --- |
| [Normalization](guide/normalization.md) | `normalize()` | `rules` | none |
| [Tokenization](guide/tokens-and-sentences.md) | `tokenize()` | `rules` | none |
| [Sentence splitting](guide/tokens-and-sentences.md) | `sentences()` | `rules` | none |
| [Stemming](guide/stemming.md) | `stem()` | `suffix`, `dictionary` | suffix list, stem dictionary |
| [Legacy fonts](guide/legacy-fonts.md) | `from_legacy_font()` | `fm` | none |
| [Akshara segmentation](guide/normalization.md#aksharas) | `aksharas()` | — | none |

Every task function has the same shape: the text first, then keyword-only `backend=`,
`normalize=` and backend options. Other packages can add backends as
[plugins](guide/plugins.md). Accuracy on public test sets is reported in
[Evaluation](guide/evaluation.md).

## License

Apache License 2.0.
