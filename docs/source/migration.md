# Migrating from 0.3

Sinling 0.4 is a redesign, and the 0.3 API is gone. If you can't move yet, pin the old version:

```
pip install "sinling<0.4"
```

## Where things went

| 0.3 | 0.4 |
| --- | --- |
| `SinhalaTokenizer().tokenize(sentence)` | `sinling.tokenize(text)` |
| `SinhalaTokenizer().split_sentences(text)` | `sinling.sentences(text)` |
| `SinhalaTweetTokenizer().tokenize(tweet)` | `sinling.tokenize(text)`: URLs, mentions, hashtags and emoji are single tokens |
| `SinhalaStemmer().stem(word)` | `sinling.stem(text)`, or `(stem, suffix)` for one word as shown below |
| `preprocess(text)` | `sinling.normalize(text)` |
| `POSTagger().predict(sentences)` | not in 0.4 yet; pin `sinling<0.4` |
| `word_joiner.join(a, b)` | not in 0.4; pin `sinling<0.4` |
| `word_splitter.split(word)` | not in 0.4; pin `sinling<0.4` |

0.3's `SinhalaStemmer().stem(word)` returned `(base, suffix)` and used the stem dictionary by
default. In 0.4 the default backend is `suffix`; to get the 0.3 behaviour for one word:

```python
from sinling.registry import get_backend

stemmer = get_backend("stem", "dictionary")
stemmer.split("අංකයක්")  # ('අංක', 'යක්')
```

## Behaviour changes

**Tokenization**

- Strings are normalized before tokenizing. Pass `normalize=False` for 0.3's behaviour.
- The tokenizer no longer deletes characters. 0.3 removed about 80, including accented Latin
  letters such as `é` and `ñ`.
- Abbreviations keep their full stop only at the start of a word. In 0.3, a sentence ending in
  `ගව.` kept the full stop on the word and never ended.
- Numbers such as `3.14`, `1,000` and `10:30` are single tokens. 0.3 treated `0.` to `9.` as
  abbreviations, so `10.` at the end of a sentence didn't end it.
- Words that are also abbreviations, such as `ඒ`, keep a following full stop only inside a chain
  like `ඒ.බී.`.

**Sentences**

- A colon or semicolon no longer ends a sentence; blank lines and list items now do.
- `return_sinhala_only=` is gone; filter the result yourself if you need it.

**Stemming**

- The stemmer's data is downloaded on first use instead of being part of the package. See
  [Downloads and offline use](guide/downloads.md).
- The suffix stemmer gives the same results as 0.3.7 on all 27,206 words tested. The dictionary
  stemmer differs only for input that isn't in Unicode NFC, which 0.4 normalizes first.

**Normalization**

- 0.3's `preprocess()` joined `උ` + `ෘ` into `ඌ`, which is wrong; `ඌ` is `උ` + `ෟ`.
  `normalize()` follows the Unicode Standard.

**Packaging**

- Python 3.11 or newer.
- No dependencies: `nltk`, `scikit-learn-crfsuite`, `joblib`, `pygtrie` and `emoji` are no
  longer needed.
- The wheel is about 35 KB instead of 20 MB.
