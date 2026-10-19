# Sinling

A language processing toolkit for Sinhala (සිංහල).

[![PyPI version](https://badge.fury.io/py/sinling.svg)](https://badge.fury.io/py/sinling)

> **Sinling 0.4 is in development.** It is a redesign with a new API and is **not compatible
> with 0.3**. 0.4 pre-releases install only when you ask for them (`pip install --pre sinling`).
>
> If your code uses the 0.3 API (`SinhalaTokenizer`, `SinhalaStemmer`, `POSTagger`,
> `word_joiner`, `word_splitter`, `preprocess`), pin the version: `pip install "sinling<0.4"`,
> or `sinling<0.4` in `requirements.txt`. The 0.3 documentation is in the
> [0.3.7 README](https://github.com/ysenarath/sinling/blob/v0.3.7/README.md).

## Installation

```
pip install --pre sinling
```

Sinling 0.4 needs Python 3.11 or newer and has no dependencies.

## Quick start

```python
>>> import sinling

>>> sinling.normalize("\N{SINHALA VOWEL SIGN KOMBUVA}ගදර\N{NO-BREAK SPACE}යනවා")
'ගෙදර යනවා'

>>> print(" / ".join(sinling.aksharas("ශ්‍රී ලංකාව")))
ශ්‍රී /   / ලං / කා / ව

```

## Normalization

Sinhala text reaches you in many encodings of the same words: typed in visual order, copied
from PDFs, pasted with invisible characters. `sinling.normalize()` converts it to one canonical
Unicode form. It applies these rules in order:

1. **Invisible characters** — removes zero-width spaces, byte order marks, soft hyphens, word
   joiners and direction marks.
2. **Joiners** — puts each zero-width joiner (ZWJ) where SLS 1134 expects it for yansaya,
   rakaransaya, repaya and touching letters, and drops stray ZWJ and ZWNJ. Joiners in emoji
   sequences are left alone.
3. **Doubled signs** — two kombuvas typed for kombu deka become `ෛ`; the same for `ෲ` and `ෳ`.
4. **Visual order** — moves a vowel sign typed before its consonant (`ෙ` + `ක`) after it.
5. **Vowel letters** — replaces sequences such as `අ` + `ා` with `ආ`, following the Unicode
   Standard's list of sequences not to use.
6. **NFC** — Unicode normalization, which merges two-part vowel signs such as `ෙ` + `ා` into `ො`.
7. **Whitespace** — turns runs of spaces, tabs and other Unicode spaces into one space and
   trims each line. Line breaks are kept.

Two presets are available. `"standard"` (the default) is safe for display and storage.
`"search"` also strips every ZWJ next to Sinhala letters, so spelling variants match. Turn a
single rule off by name:

```python
>>> sinling.normalize("ශ්‍රී", preset="search") == "ශ්රී"
True

>>> sinling.normalize("  \N{SINHALA VOWEL SIGN KOMBUVA}ගදර  ", reorder=False, whitespace="keep")
'  ෙගදර  '

```

The options are `invisible`, `zwj` (`"canonical"`, `"strip"` or `"keep"`), `doubled_signs`,
`reorder`, `vowel_letters`, `nfc` and `whitespace` (`"collapse"` or `"keep"`).

## Tokens and sentences

```python
>>> sinling.tokenize("පෙ.ව. 10ට රු.500ක් ගෙවන්න.")
['පෙ.ව.', '10ට', 'රු.', '500ක්', 'ගෙවන්න', '.']

>>> sinling.sentences('ඔහු කීවේ "මම එනවා." ඊට පසු ගියේය.')
['ඔහු කීවේ "මම එනවා."', 'ඊට පසු ගියේය.']

```

Strings are normalized before tokenizing; pass `normalize=False` to skip that. Tokenizing never
changes the text. Each token records its kind in `token.attrs["kind"]`: `word`, `number`,
`punct`, `symbol`, `abbreviation`, `url`, `email`, `mention`, `hashtag`, `emoji` or `other`.
Known abbreviations such as `පෙ.ව.` and `රු.` keep their full stop; add your own with
`extra_abbreviations=[...]`.

A sentence ends after `.` `?` `!` `…` or the kunddaliya `෴`, at a blank line, and before a
list item. A number and full stop at the start of a line (`1.`) is a list marker, not a
sentence end.

## Stemming

```python
sinling.stem("පොත්වලින් කියවන්න.")                         # ['පොත', 'කියව', '.']
sinling.stem("පිහිටවීමට", backend="dictionary")            # ['පිහිටවීම']
```

The default `suffix` backend strips the longest known suffix. The `dictionary` backend looks
words up in a 27,197-word stem dictionary first. Only word tokens are stemmed; in a pipeline,
each token also gets `attrs["stem"]` and `attrs["suffix"]`.

The stemmer and its data come from the
[sinhala-stemmer](https://github.com/rksk/sinhala-news-analysis/tree/master/sinhala-stemmer)
of the Sinhala News Analysis project; please cite it if you use them. Its repository has no
licence, so Sinling does not ship the data: the suffix list (6 KB) and the stem dictionary
(1.3 MB) are downloaded from that repository on first use, pinned to one commit and checked
against a SHA-256 checksum.

## Legacy fonts

Many Sinhala PDFs and Word files still use legacy fonts such as FMAbhaya, which draw Sinhala
letters on Latin characters, so extracted text reads as gibberish. `from_legacy_font()`
converts it to Unicode and then normalizes it:

```python
>>> sinling.from_legacy_font('jd;h" c,h" wdydr')
'වාතය, ජලය, ආහාර'

>>> sinling.from_legacy_font("fomd\xbe;f\xefka;=j")
'දෙපාර්තමේන්තුව'

```

The `fm` backend covers the FM font family (FMAbhaya, FMMalithi, FMEmanee, FMAbabld and others
that share the Wijesekara layout). It matched the original converter on 2.8 million characters
of text extracted from school textbooks. Only convert text that is actually in a legacy font,
because Latin letters and punctuation are remapped; in a PDF, pick the spans whose font
`sinling.legacy_fonts.is_fm_font(name)` accepts. Characters without a mapping are kept and
counted in `doc.meta["legacy_font_unmapped"]`. DL fonts and Tamil legacy fonts are planned.

## Documents, pipelines and offsets

Task functions such as `normalize()` return plain values. To run several steps and keep
everything, use a pipeline, which returns a `Doc`. `sinling.pipeline()` with no steps runs
normalize, tokenize and sentences. A `Doc` keeps the original text, the working
text and an alignment between them, so any result can be traced back to the input:

```python
>>> nlp = sinling.pipeline(["normalize"])
>>> doc = nlp("\N{ZERO WIDTH SPACE}මම\N{NO-BREAK SPACE}\N{NO-BREAK SPACE}\N{SINHALA VOWEL SIGN KOMBUVA}ගදර")
>>> doc.text
'මම ගෙදර'
>>> start, end = doc.to_raw(3, 7)  # 'ගෙදර' in the normalized text
>>> doc.raw[start:end] == "\N{SINHALA VOWEL SIGN KOMBUVA}ගදර"
True

```

A `Doc` also holds tokens, sentences and labelled spans, and converts to and from JSON with
`doc.to_dict()` and `Doc.from_dict()`.

## Backends and plugins

Each task can have several interchangeable backends, chosen with `backend=`:

```python
>>> [(b.name, b.default) for b in sinling.backends("normalize")]
[('rules', True)]

```

Other packages can add backends without changes to Sinling, through the `sinling.backends`
entry-point group. By convention they are published as `sinling-<name>`:

```toml
[project.entry-points."sinling.backends"]
"normalize.mybackend" = "sinling_mybackend:MyNormalizer"
```

A plugin is imported only when one of its backends is first used. Plugin authors subclass
`sinling.Backend` and find the rest of the registry in `sinling.registry`. `sinling.backends()`
also lists what each backend downloads on first use; an empty list means it works offline from
the start.

## Resources and offline use

Models and dictionaries are downloaded on first use, checked against a SHA-256 checksum and
cached in `~/.cache/sinling`. Set `SINLING_HOME` to use another directory, and
`SINLING_OFFLINE=1` to forbid downloads. To prepare an offline machine, fetch what you need on a
connected one and copy the cache directory over:

```python
sinling.download("sinhala-suffixes")         # for the suffix stemmer
sinling.download("sinhala-stem-dictionary")  # for the dictionary stemmer
```

`normalize`, `tokenize` and `sentences` need no downloads.

## Accuracy

Every backend is scored on public test sets. These are the default backends on the two
[Universal Dependencies](https://universaldependencies.org/) Sinhala treebanks (release 2.18):

| Task | Backend | Dataset | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- |
| tokenize | rules | [UD Sinhala STB](https://universaldependencies.org/treebanks/si_stb) (100 sentences) | 1.000 | 1.000 | 1.000 |
| tokenize | rules | [UD Sinhala Appuwa](https://universaldependencies.org/treebanks/si_appuwa) (69 sentences) | 0.994 | 0.997 | 0.996 |
| sentences | rules | UD Sinhala STB | 1.000 | 1.000 | 1.000 |
| sentences | rules | UD Sinhala Appuwa | 0.958 | 1.000 | 0.979 |

The treebanks put a space around every punctuation mark, so their text is detokenized first
(`. , ? ! : ;` and closing brackets are joined to the word before them). Tokens are scored by
their exact character spans, sentences by where they end. Most of the remaining differences are
annotation choices in Appuwa: two tokens keep their punctuation attached (`නැහැ,`), and three
sentences contain a full stop inside them, where the splitter ends a sentence. The test sets are
small, so treat these numbers as a check, not a ranking.

Reproduce the table, or score a backend on your own CoNLL-U file:

```
python -m sinling evaluate
python -m sinling evaluate --task tokenize --dataset my-test-set.conllu
```

```python
report = sinling.evaluate("sentences", "ud-sinhala-appuwa")
print(report.f1, report.counts)
```

The treebanks are licensed CC BY-SA 4.0 and are downloaded on first use. If you use them, cite
Liyanage, Sarveswaran et al. (2023), *Sinhala Dependency Treebank (STB)*, UDW 2023, and the
UD Sinhala Appuwa treebank.

## Roadmap

0.4 is being built in milestones:

- **0.4.0a1** — core API, `Doc`, pipelines, plugins, `normalize()` and akshara segmentation.
- **0.4.0a2** — tokenization, sentence splitting and stemming on the new core, legacy FM font
  to Unicode conversion, the first downloadable resources.
- **0.4.0** — documentation in Sinhala and English, an evaluation harness, a stable API.

## Development

```
pip install .
python -P -m unittest discover -s tests -t tests
```

The tests import the installed package, not the source tree. Every push is tested on
Python 3.11 to 3.14.

## License

Apache License 2.0. See [LICENSE](LICENSE).
