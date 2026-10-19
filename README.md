# Sinling

A toolkit for working with Sinhala (සිංහල) text in Python. It cleans up text, splits it into
words and sentences, finds word stems, and turns text typed in old Sinhala fonts into proper
Unicode.

[![PyPI version](https://badge.fury.io/py/sinling.svg)](https://badge.fury.io/py/sinling)

> **Sinling 0.4 is in development.** It works differently from 0.3, so code written for 0.3
> won't run on it. A plain `pip install sinling` still installs 0.3; to try 0.4, use
> `pip install --pre sinling`.
>
> If your code uses `SinhalaTokenizer`, `SinhalaStemmer`, `POSTagger`, `word_joiner`,
> `word_splitter` or `preprocess`, keep using 0.3 with `pip install "sinling<0.4"` (or
> `sinling<0.4` in `requirements.txt`). The 0.3 documentation is in the
> [0.3.7 README](https://github.com/ysenarath/sinling/blob/v0.3.7/README.md).

## Installation

```
pip install --pre sinling
```

You need Python 3.11 or newer. Nothing else is installed with it.

## Quick start

```python
>>> import sinling

>>> sinling.normalize("\N{SINHALA VOWEL SIGN KOMBUVA}ගදර\N{NO-BREAK SPACE}යනවා")
'ගෙදර යනවා'

>>> print(" / ".join(sinling.aksharas("ශ්\N{ZERO WIDTH JOINER}රී ලංකාව")))
ශ්‍රී /   / ලං / කා / ව

```

## Cleaning up text

The same Sinhala word can be stored in different ways: typed with a vowel sign in the wrong
order, copied from a PDF, or pasted with invisible characters inside. The words look the same,
but a computer treats them as different, so search and word counts go wrong. `normalize()`
cleans up the text so that the same word is always stored the same way. It:

- removes invisible characters such as zero-width spaces;
- puts the joiner used in `ක්‍ය`, `ක්‍ර` and `ර්‍ක` where the Sinhala Unicode standard expects it,
  and removes joiners that don't belong;
- turns two kombuvas into kombu deka (`ෛ`);
- moves a kombuva typed before its letter to after it;
- replaces a vowel letter plus a sign, such as `අ` + `ා`, with the single letter `ආ`;
- joins vowel signs typed in two parts;
- tidies up spaces.

For search, `preset="search"` also removes the joiners, so `ශ්‍රී` and `ශ්රී` match. You can turn
off any fix by name:

```python
>>> sinling.normalize("ශ්\N{ZERO WIDTH JOINER}රී", preset="search") == "ශ්රී"
True

>>> sinling.normalize("  ගම  ", whitespace="keep")
'  ගම  '

```

## Words and sentences

```python
>>> sinling.tokenize("පෙ.ව. 10ට රු.500ක් ගෙවන්න.")
['පෙ.ව.', '10ට', 'රු.', '500ක්', 'ගෙවන්න', '.']

>>> sinling.sentences('ඔහු කීවේ "මම එනවා." ඊට පසු ගියේය.')
['ඔහු කීවේ "මම එනවා."', 'ඊට පසු ගියේය.']

```

Text is cleaned up first, and the words are always exact pieces of it. Common abbreviations
such as `පෙ.ව.` and `රු.` keep their full stop; add your own with `extra_abbreviations=[...]`.
A sentence ends after `.` `?` `!` `…` or `෴`, at a blank line, or before a new list item.

## Word stems

```python
sinling.stem("පොත්වලින් කියවන්න.")                 # ['පොත', 'කියව', '.']
sinling.stem("පිහිටවීමට", backend="dictionary")    # ['පිහිටවීම']
```

By default `stem()` removes the longest ending it knows. With `backend="dictionary"` it looks the
word up in a 27,197-word dictionary first.

The stemmer and its data come from the
[sinhala-stemmer](https://github.com/rksk/sinhala-news-analysis/tree/master/sinhala-stemmer)
of the Sinhala News Analysis project; please cite it if you use it. Their data has no licence, so
it isn't included in Sinling. It is downloaded from their repository the first time you use the
stemmer, always the same version, and checked to make sure it arrived intact.

## Old Sinhala fonts

Many Sinhala PDFs and Word files use old fonts such as FMAbhaya, which show Sinhala letters in
place of English ones. Copied text then reads as gibberish. `from_legacy_font()` turns it into
proper Unicode Sinhala:

```python
>>> sinling.from_legacy_font('jd;h" c,h" wdydr')
'වාතය, ජලය, ආහාර'

>>> sinling.from_legacy_font("fomd\xbe;f\xefka;=j")
'දෙපාර්තමේන්තුව'

```

It supports the FM fonts (FMAbhaya, FMMalithi, FMEmanee, FMAbabld and others) and was tested on
2.8 million characters from school textbooks. Convert only text that is in an old font, because
English letters are turned into Sinhala ones. DL fonts and old Tamil fonts are planned.

## Doing several things at once

A pipeline runs several steps on your text and gives you a `Doc` with all the results. The `Doc`
also remembers where each word was in your original text, even after clean-up:

```python
>>> doc = sinling.pipeline()("\N{ZERO WIDTH SPACE}මම යනවා. ඔයා එනවා.")
>>> [token.text for token in doc.tokens]
['මම', 'යනවා', '.', 'ඔයා', 'එනවා', '.']
>>> start, end = doc.to_raw(doc.tokens[1])
>>> doc.raw[start:end]
'යනවා'

```

## Choosing how a task is done

Some tasks can be done in more than one way. Choose with `backend="..."`, and see the options
with `sinling.backends()`:

```python
>>> [(b.name, b.default) for b in sinling.backends("stem")]
[('dictionary', False), ('suffix', True)]

```

Other packages can add more ways as plugins, published on PyPI as `sinling-<name>`.

## Downloads and offline use

Cleaning up text, splitting it, and converting old fonts work without the internet. The stemmer
downloads its data the first time you use it, into `~/.cache/sinling`. To use it on a computer
without internet, download it on another computer and copy that folder over:

```python
sinling.download("sinhala-suffixes")
sinling.download("sinhala-stem-dictionary")
```

Set `SINLING_HOME` to save downloads elsewhere, and `SINLING_OFFLINE=1` to make sure Sinling
never connects.

## Accuracy

Tested on the two Sinhala treebanks of [Universal Dependencies](https://universaldependencies.org/),
collections of sentences split into words by hand:

| Task | Test data | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| Splitting into words | [UD Sinhala STB](https://universaldependencies.org/treebanks/si_stb) (100 sentences) | 1.000 | 1.000 | 1.000 |
| Splitting into words | [UD Sinhala Appuwa](https://universaldependencies.org/treebanks/si_appuwa) (69 sentences) | 0.994 | 0.997 | 0.996 |
| Splitting into sentences | UD Sinhala STB | 1.000 | 1.000 | 1.000 |
| Splitting into sentences | UD Sinhala Appuwa | 0.958 | 1.000 | 0.979 |

1.000 is perfect. Most of the remaining differences come from how the Appuwa sentences were
marked up. The test sets are small, so treat these numbers as a check rather than a precise
measure. Run the tests yourself with `python -m sinling evaluate`, or on your own data in CoNLL-U
format with `--task tokenize --dataset my-file.conllu`.

The test data is licensed CC BY-SA 4.0 and downloaded the first time you run a test. If you
publish results on it, please cite Liyanage, Sarveswaran et al. (2023), *Sinhala Dependency
Treebank (STB)*, UDW 2023, and the UD Sinhala Appuwa treebank.

## What's next

- **0.4.0a1**: text clean-up and akshara splitting.
- **0.4.0a2**: splitting into words and sentences, word stems, old FM fonts, accuracy tests.
- **0.4.0**: a documentation website in Sinhala and English.

## Contributing

```
pip install .
python -P -m unittest discover -s tests -t tests
```

The tests run against the installed package, and every change is tested on Python 3.11 to 3.14.

## License

Apache License 2.0. See [LICENSE](LICENSE).
