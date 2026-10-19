# ප්ලගිනයක් ලිවීම

Sinling වෙනස් නොකර ඕනෑම පැකේජයකට Sinling කාර්යයකට backend එකක් එක් කළ හැකිය. ඉන්පසු
පරිශීලකයින් එය `backend=` මගින්, හරියටම ගොඩනැගූ backend එකක් ලෙසම තෝරා ගනී.

## 1. Backend එක ලියන්න {#1-write-the-backend}

Backend එකක් `sinling.Backend` හි උප-පන්තියකි. එහි විකල්ප keyword arguments ලෙස ලැබේ;
`__call__` එකට `Doc` එකක් ලැබී, එය සටහන් කර, ආපසු ලබා දෙයි.

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

Backend එකකට කළ හැකි දේ එහි කාර්යය මත රඳා පවතී:

| කාර්යය | Backend එක කළ යුත්තේ |
| --- | --- |
| `normalize`, `legacy_font` | පෙළ වෙනස් කළ යුත්තේ සම්බන්ධතාව රඳවා ගන්නා `doc.edit_text()` මගින් පමණි. |
| `tokenize` | ස්ථානවල ඇති `doc.text` සමඟ පෙළ ගැළපෙන ටෝකන සමඟ `doc.set_tokens()` කැඳවන්න. |
| `sentences` | `doc.sents` ටෝකන දර්ශක span ලෙස සකසන්න. |
| `stem` | සෑම ටෝකනයකම `attrs["stem"]` සහ `attrs["suffix"]` සකසන්න. |

## 2. එයට අවශ්‍ය දේ ප්‍රකාශ කරන්න {#2-declare-what-it-needs}

පන්ති ගුණාංග Sinling ට backend එක රඳා පවතින්නේ කුමක් මතදැයි කියයි:

```python
class TransformerNER(Backend):
    extra = "hf"                        # the extra that installs its dependencies
    requires = ("transformers",)        # modules it imports
    resources = ("my-ner-model",)       # resources it downloads on first use
```

අවශ්‍ය module එකක් නැති නම්, Sinling `pip install` විධානය සමඟ `MissingDependencyError` මතු
කරයි. බාගත හැකි ගොනු `sinling.resources.register_resource()` මගින්, අනුවාදයට සහ SHA-256 ට
සවි කර ලියාපදිංචි කර, `sinling.resources.resource_path()` මගින් පූරණය කරන්න.

## 3. එය ලියාපදිංචි කරන්න {#3-register-it}

ප්ලගිනයේ `pyproject.toml` වෙත entry point එකක් එක් කරන්න. නාමය `<task>.<backend>` වේ:

```toml
[project.entry-points."sinling.backends"]
"tokenize.whitespace" = "sinling_whitespace:WhitespaceTokenizer"
```

Backend එකක් පළමු වරට සොයන විට Sinling entry points කියවයි, නමුත් ප්ලගිනය import කරන්නේ එහි
backend එකක් භාවිත කරන විට පමණි; ඒ නිසා ස්ථාපිත ප්ලගිනයක් එතෙක් කිසිදු වියදමක් නොකරයි. සම්මතය
ලෙස, ප්ලගින PyPI හි `sinling-<name>` ලෙස ප්‍රකාශයට පත් කරන්න.

## 4. එය භාවිත කර ඇගයීම {#4-use-and-evaluate-it}

```python
sinling.tokenize("මම ගෙදර යනවා.", backend="whitespace")
sinling.evaluate("tokenize", "ud-sinhala-stb", backend="whitespace")
```

`sinling.backends("tokenize")` එය ගොඩනැගූ backends අසලින් ලැයිස්තුගත කරයි. පළමු භාවිතයට පෙර,
එහි විස්තර (extra, බාගැනීම්, ලබා ගත හැකි බව) `None` ලෙස පෙන්වයි.
