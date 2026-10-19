# Stemming

`stem()` finds the stem of each word: the part left after removing endings like `වලින්` or
`ට`. Punctuation and other non-words are returned as they are.

```python
sinling.stem("පොත්වලින් කියවන්න.")                 # ['පොත', 'කියව', '.']
sinling.stem("පිහිටවීමට", backend="dictionary")    # ['පිහිටවීම']
```

## Two ways to find stems

| `backend=` | How it works | Downloads on first use |
| --- | --- | --- |
| `suffix` (default) | Removes the longest ending it knows. | a list of endings (6 KB) |
| `dictionary` | Looks the word up in a dictionary of 27,197 words first, then removes endings. | the list of endings and the dictionary (1.3 MB) |

The dictionary sometimes gives a different spelling as the stem, such as ඉන්දීය → ඉන්දියාව.
Words written with a joined letter, like `ප්‍රශ්නයට`, are found in the dictionary too.

In a pipeline, each token also gets its stem and the ending that was removed:

```python
nlp = sinling.pipeline(["normalize", "tokenize", "stem"])
doc = nlp("පොත්වලින් 500ක්")
[(t.attrs["stem"], t.attrs["suffix"]) for t in doc.tokens]
# [('පොත', '්වලින්'), ('500', 'ක්')]
```

An ending can start with a vowel sign or an al-lakuna, so a stem can end in the middle of a
syllable, as in `පිහිටවීමට` → `පිහිටව` + `ීමට`. Stemming won't make search much better on its
own; in our tests it made little difference.

## Where the data comes from

The stemmer and its data come from the
[sinhala-stemmer](https://github.com/rksk/sinhala-news-analysis/tree/master/sinhala-stemmer)
of the Sinhala News Analysis project. Please cite it if you use the stemmer. Its authors note
that the dictionary is unfinished and has errors.

Their data has no licence, so it isn't included in Sinling. It is downloaded from their
repository the first time you use the stemmer, always the same version, and checked to make
sure it arrived intact. To use the stemmer without internet, see
[Downloads and offline use](downloads.md).
