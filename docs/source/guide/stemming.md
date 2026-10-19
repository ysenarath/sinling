# Stemming

`stem()` reduces each word token to its stem. Other tokens, such as punctuation, keep their text.

```python
sinling.stem("පොත්වලින් කියවන්න.")                 # ['පොත', 'කියව', '.']
sinling.stem("පිහිටවීමට", backend="dictionary")    # ['පිහිටවීම']
```

## Backends

| Backend | How it works | Downloads |
| --- | --- | --- |
| `suffix` (default) | Strips the longest known suffix. A word that is itself a suffix is left as it is. | suffix list (6 KB) |
| `dictionary` | Looks the word up in a 27,197-word stem dictionary first, then strips suffixes. | suffix list and stem dictionary (1.3 MB) |

When the dictionary's stem is a different spelling (ඉන්දීය → ඉන්දියාව), the stem is returned
with an empty suffix. Dictionary lookups ignore zero-width joiners, so `ප්‍රශ්නයට` matches the
dictionary's `ප්රශ්නයට`, and the joiner is kept in the stem.

In a pipeline, each token gets `attrs["stem"]` and `attrs["suffix"]`:

```python
nlp = sinling.pipeline(["normalize", "tokenize", "stem"])
doc = nlp("පොත්වලින් 500ක්")
[(t.attrs["stem"], t.attrs["suffix"]) for t in doc.tokens]
# [('පොත', '්වලින්'), ('500', 'ක්')]
```

Suffixes can start with a vowel sign or an al-lakuna, so a stem may end in the middle of an
akshara (`පිහිටවීමට` → `පිහිටව` + `ීමට`). This is how the original algorithm works.

## Where the data comes from

The algorithm and both data files come from the
[sinhala-stemmer](https://github.com/rksk/sinhala-news-analysis/tree/master/sinhala-stemmer)
of the Sinhala News Analysis project. Please cite it if you use the stemmer. Its authors note
that the stem dictionary is not complete and contains errors.

That repository has no licence, so Sinling does not ship the data. Both files are downloaded
from the authors' repository on first use, pinned to commit `05e7076` and checked against a
SHA-256 checksum. See [Downloads and offline use](downloads.md) to prepare a machine without
internet access.

In tests on SinhalaMMLU textbook retrieval, stemming barely changed retrieval quality, so
don't expect it to improve search by itself.
