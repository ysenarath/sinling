# Writing a plugin

Any package can add a backend to a Sinling task without changing Sinling. Users then choose it
with `backend=`, exactly like a built-in one.

## 1. Write the backend

A backend subclasses `sinling.Backend`. Its options arrive as keyword arguments, and
`__call__` receives a `Doc`, annotates it and returns it.

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

What a backend may do depends on its task:

| Task | The backend must |
| --- | --- |
| `normalize`, `legacy_font` | Change the text only through `doc.edit_text()`, which keeps the alignment. |
| `tokenize` | Call `doc.set_tokens()` with tokens whose text matches `doc.text` at their offsets. |
| `sentences` | Set `doc.sents` to spans of token indices. |
| `stem` | Set `attrs["stem"]` and `attrs["suffix"]` on each token. |

## 2. Declare what it needs

Class attributes tell Sinling what the backend depends on:

```python
class TransformerNER(Backend):
    extra = "hf"                        # the extra that installs its dependencies
    requires = ("transformers",)        # modules it imports
    resources = ("my-ner-model",)       # resources it downloads on first use
```

If a required module is missing, Sinling raises `MissingDependencyError` with the
`pip install` command. Register downloadable files with `sinling.resources.register_resource()`,
pinned by version and SHA-256, and load them with `sinling.resources.resource_path()`.

## 3. Register it

Add an entry point to the plugin's `pyproject.toml`. The name is `<task>.<backend>`:

```toml
[project.entry-points."sinling.backends"]
"tokenize.whitespace" = "sinling_whitespace:WhitespaceTokenizer"
```

Sinling reads entry points the first time a backend is looked up, but imports the plugin only
when one of its backends is used, so an installed plugin costs nothing until then. By
convention, publish plugins on PyPI as `sinling-<name>`.

## 4. Use and evaluate it

```python
sinling.tokenize("මම ගෙදර යනවා.", backend="whitespace")
sinling.evaluate("tokenize", "ud-sinhala-stb", backend="whitespace")
```

`sinling.backends("tokenize")` lists it next to the built-in backends. Before it is first
used, its details (extra, downloads, availability) show as `None`.
