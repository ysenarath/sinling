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

## Documents, pipelines and offsets

Task functions such as `normalize()` return plain values. To run several steps and keep
everything, use a pipeline, which returns a `Doc`. A `Doc` keeps the original text, the working
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

A plugin is imported only when one of its backends is first used.

## Resources and offline use

Larger models and dictionaries will be downloaded on first use, checked against a SHA-256
checksum and cached in `~/.cache/sinling`. Set `SINLING_HOME` to use another directory, and
`SINLING_OFFLINE=1` to forbid downloads. Fetch a resource ahead of time with
`sinling.download(name)`. No resources are published yet.

## Roadmap

0.4 is being built in milestones:

- **0.4.0a1** — core API, `Doc`, pipelines, plugins, `normalize()` and akshara segmentation.
- **0.4.0a2** — tokenization and stemming on the new core, legacy FM font to Unicode
  conversion, the first downloadable resources.
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
