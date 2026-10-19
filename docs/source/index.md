# Sinling

Sinling is a toolkit for working with Sinhala (සිංහල) text in Python. It cleans up text, splits
it into words and sentences, finds word stems, and turns text typed in old Sinhala fonts into
proper Unicode.

!!! warning "Sinling 0.4 is a pre-release"
    0.4 is a new version that works differently from 0.3. A plain `pip install sinling` still
    installs 0.3. If your code was written for 0.3, keep using it with `sinling<0.4`, or see the
    [migration guide](migration.md) to update it.

## Installation

```
pip install --pre sinling
```

You need Python 3.11 or newer. Nothing else is installed with it.

## Quick start

Each task is a single function. Give it text, and you get back text or a list:

```python
>>> import sinling

>>> sinling.normalize("\N{SINHALA VOWEL SIGN KOMBUVA}ගදර\N{NO-BREAK SPACE}යනවා")
'ගෙදර යනවා'

>>> sinling.tokenize("පෙ.ව. 10ට රු.500ක් ගෙවන්න.")
['පෙ.ව.', '10ට', 'රු.', '500ක්', 'ගෙවන්න', '.']

>>> sinling.sentences("මම ගෙදර යනවා. ඔයා එනවද?")
['මම ගෙදර යනවා.', 'ඔයා එනවද?']

```

To do several things at once, use a pipeline. It gives you a `Doc` that holds the words and
sentences, and remembers where each one was in your original text:

```python
>>> doc = sinling.pipeline()("මම ගෙදර යනවා. ඔයා එනවද?")
>>> [token.text for token in doc.tokens]
['මම', 'ගෙදර', 'යනවා', '.', 'ඔයා', 'එනවද', '?']
>>> len(doc.sents)
2

```

## What you can do

| Task | Function | Ways to do it (`backend=`) | Needs a download |
| --- | --- | --- | --- |
| [Clean up text](guide/normalization.md) | `normalize()` | `rules` | no |
| [Split into words](guide/tokens-and-sentences.md) | `tokenize()` | `rules` | no |
| [Split into sentences](guide/tokens-and-sentences.md) | `sentences()` | `rules` | no |
| [Find word stems](guide/stemming.md) | `stem()` | `suffix`, `dictionary` | yes, on first use |
| [Convert old fonts](guide/legacy-fonts.md) | `from_legacy_font()` | `fm` | no |
| [Split into aksharas](guide/normalization.md#aksharas) | `aksharas()` | — | no |

All the functions work the same way. Pass your text first. Add `backend="..."` to choose a
different way of doing the task, or `normalize=False` to skip the automatic clean-up. Other
packages can add more ways as [plugins](guide/plugins.md), and
[Evaluation](guide/evaluation.md) shows how accurate each one is.

## License

Apache License 2.0.
