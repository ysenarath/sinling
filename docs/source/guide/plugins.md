# Writing a plugin

Sinling can do some tasks in more than one way, and each way is called a backend. You can add
your own backend in a separate package, without changing Sinling. People then choose it with
`backend=`, just like the built-in ones.

## 1. Write the backend

A backend is a class based on `sinling.Backend`. Its options arrive as keyword arguments.
Sinling calls it with a `Doc`; the backend adds its results to the `Doc` and returns it.

```python
# sinling_whitespace/__init__.py
from sinling import Backend, Doc, Token


class WhitespaceTokenizer(Backend):
    """Splits on whitespace only."""

    def __call__(self, doc: Doc) -> Doc:
        tokens, pos = [], 0
        for part in doc.text.split():
            start = doc.text.index(part, pos)
            tokens.append(Token(part, start, start + len(part), {"kind": "word"}))
            pos = start + len(part)
        doc.set_tokens(tokens)
        return doc
```

What the backend has to do depends on its task:

| Task | What the backend does |
| --- | --- |
| `normalize`, `legacy_font` | Changes the text, but only through `doc.edit_text()`, so positions in the original text stay known. |
| `tokenize` | Calls `doc.set_tokens()` with the tokens it found. |
| `sentences` | Sets `doc.sents`. |
| `stem` | Sets `attrs["stem"]` and `attrs["suffix"]` on each token. |

## 2. Declare what it needs

If the backend needs other packages or data, say so in the class:

```python
class TransformerNER(Backend):
    extra = "hf"                        # the extra that installs its dependencies
    requires = ("transformers",)        # modules it imports
    resources = ("my-ner-model",)       # resources it downloads on first use
```

If a package it needs isn't installed, the user gets an error with the `pip install` command
to fix it. To download data files on first use, register them with
`sinling.resources.register_resource()` and open them with `sinling.resources.resource_path()`.

## 3. Register it

Tell Sinling about the backend in your package's `pyproject.toml`. The name is
`<task>.<backend>`:

```toml
[project.entry-points."sinling.backends"]
"tokenize.whitespace" = "sinling_whitespace:WhitespaceTokenizer"
```

Installing a plugin doesn't slow Sinling down: the plugin is loaded only when someone uses it.
Please publish plugins on PyPI with a name starting `sinling-`, such as `sinling-whitespace`.

## 4. Use and evaluate it

```python
sinling.tokenize("මම ගෙදර යනවා.", backend="whitespace")
sinling.evaluate("tokenize", "ud-sinhala-stb", backend="whitespace")
```

`sinling.backends("tokenize")` lists it next to the built-in backends.
