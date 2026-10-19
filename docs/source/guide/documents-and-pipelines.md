# Documents and pipelines

Functions like `tokenize()` give you a simple list. When you need more, such as the words with
their positions, the sentences and the stems, use a pipeline. It runs several steps on your text
and gives you a `Doc` with all the results.

```python
>>> import sinling
>>> nlp = sinling.pipeline(["normalize", "tokenize", "sentences"])
>>> doc = nlp("\N{ZERO WIDTH SPACE}මම යනවා. ඔයා එනවා.")

```

`sinling.pipeline()` on its own runs these same three steps. Create a pipeline once and reuse
it for all your texts; that's faster than creating a new one each time.

## What's in a Doc

| Attribute | What it holds |
| --- | --- |
| `doc.raw` | Your text, exactly as you gave it. |
| `doc.text` | The text after clean-up or font conversion. |
| `doc.tokens` | The words and other tokens. Each has its `text`, its `start` and `end` position in `doc.text`, and `attrs` with extra details. |
| `doc.sents` | The sentences. |
| `doc.spans` | Other groups of words, such as names of people and places, once Sinling can find them. |
| `doc.meta` | Notes about the whole text, such as characters an old-font conversion didn't know. |

```python
>>> doc.text
'මම යනවා. ඔයා එනවා.'
>>> doc.tokens[1]
Token(text='යනවා', start=3, end=7, attrs={'kind': 'word'})
>>> doc.span_text(doc.sents[1])
'ඔයා එනවා.'

```

## Finding results in your original text

Cleaning up and converting text can change it, but the `Doc` remembers where everything came
from. `doc.to_raw()` gives the position of a word, a sentence or any stretch of `doc.text` in
your original text, for example to highlight it:

```python
>>> start, end = doc.to_raw(doc.tokens[1])
>>> (start, end), doc.raw[start:end]
((4, 8), 'යනවා')

```

Here the original text starts with an invisible character, so every position moves by one.

## Choosing the steps

Name each step by its task. To choose how a step is done, or to give it options, use a pair or
a triple:

```python
nlp = sinling.pipeline([
    ("legacy_font", "fm"),
    ("normalize", "rules", {"preset": "search"}),
    "tokenize",
    {"task": "stem", "backend": "dictionary"},
])
```

Steps that change the text, such as clean-up and font conversion, must come first; otherwise you
get an error. So do steps that need words, such as `sentences` and `stem`, if `tokenize` hasn't
come before them.

## Saving a Doc

`doc.to_dict()` turns a `Doc` into ordinary dicts and lists that you can save as JSON.
`Doc.from_dict()` turns them back into a `Doc`, positions included:

```python
>>> import json
>>> copy = sinling.Doc.from_dict(json.loads(json.dumps(doc.to_dict())))
>>> copy.to_raw(copy.tokens[1])
(4, 8)

```
