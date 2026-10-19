# Documents and pipelines

Task functions return plain values, which is enough for most scripts. A pipeline runs several
tasks on one `Doc` and keeps everything they find.

```python
>>> import sinling
>>> nlp = sinling.pipeline(["normalize", "tokenize", "sentences"])
>>> doc = nlp("\N{ZERO WIDTH SPACE}මම යනවා. ඔයා එනවා.")

```

`sinling.pipeline()` with no steps runs exactly these three. A pipeline builds each backend
once, so reuse it for many texts.

## The Doc

| Attribute | What it holds |
| --- | --- |
| `doc.raw` | The text exactly as given. It never changes. |
| `doc.text` | The working text, after normalization or legacy-font conversion. |
| `doc.tokens` | A list of `Token`: `text`, `start` and `end` offsets into `doc.text`, and `attrs`. |
| `doc.sents` | A list of `Span`: `start` and `end` token indices, with an optional `label` and `score`. |
| `doc.spans` | Named groups of spans, e.g. `doc.spans["ents"]` for named entities. |
| `doc.meta` | Document-level results, such as unmapped legacy-font glyphs. |

```python
>>> doc.text
'මම යනවා. ඔයා එනවා.'
>>> doc.tokens[1]
Token(text='යනවා', start=3, end=7, attrs={'kind': 'word'})
>>> doc.span_text(doc.sents[1])
'ඔයා එනවා.'

```

## Offsets back to the original

Normalization and legacy-font conversion change the text, but every change is recorded.
`doc.to_raw()` maps a token, a span or a character range in `doc.text` back to `doc.raw`, so
you can highlight a result in the original document:

```python
>>> start, end = doc.to_raw(doc.tokens[1])
>>> (start, end), doc.raw[start:end]
((4, 8), 'යනවා')

```

Here the raw text starts with an invisible zero-width space, so every offset moves by one.

## Steps

A step is a task name (its default backend), a `(task, backend)` or `(task, backend, options)`
tuple, or a dict with `task`, `backend` and `config` keys:

```python
nlp = sinling.pipeline([
    ("legacy_font", "fm"),
    ("normalize", "rules", {"preset": "search"}),
    "tokenize",
    {"task": "stem", "backend": "dictionary"},
])
```

Steps that change the text (normalization, legacy-font conversion) must come before all
others; the pipeline refuses another order. Tasks that need tokens, such as `sentences` and
`stem`, raise an error if `tokenize` hasn't run.

## Saving a Doc

`doc.to_dict()` returns plain data that can be written as JSON, and `Doc.from_dict()` rebuilds
the document, alignment included:

```python
>>> import json
>>> copy = sinling.Doc.from_dict(json.loads(json.dumps(doc.to_dict())))
>>> copy.to_raw(copy.tokens[1])
(4, 8)

```
