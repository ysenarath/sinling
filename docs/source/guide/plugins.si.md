# ප්ලගිනයක් ලිවීම

Sinling ට සමහර කාර්ය ක්‍රම එකකට වඩා ගණනකින් කළ හැකි අතර, සෑම ක්‍රමයක්ම backend එකක් ලෙස
හැඳින්වේ. Sinling වෙනස් නොකර, වෙනම පැකේජයක ඔබේම backend එකක් එක් කළ හැකිය. ඉන්පසු මිනිසුන්
එය `backend=` මගින්, ගොඩනැගූ ඒවා මෙන්ම තෝරා ගනී.

## 1. Backend එක ලියන්න {#1-write-the-backend}

Backend එකක් යනු `sinling.Backend` මත පදනම් වූ class එකකි. එහි විකල්ප keyword arguments ලෙස
ලැබේ. Sinling එය `Doc` එකක් සමඟ කැඳවයි; backend එක තම ප්‍රතිඵල `Doc` එකට එක් කර එය ආපසු දෙයි.

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

Backend එක කළ යුතු දේ එහි කාර්යය මත රඳා පවතී:

| කාර්යය | Backend එක කරන දේ |
| --- | --- |
| `normalize`, `legacy_font` | පෙළ වෙනස් කරයි, නමුත් `doc.edit_text()` හරහා පමණි; එවිට මුල් පෙළේ ස්ථාන නොනැසී පවතී. |
| `tokenize` | සොයා ගත් ටෝකන සමඟ `doc.set_tokens()` කැඳවයි. |
| `sentences` | `doc.sents` සකසයි. |
| `stem` | සෑම ටෝකනයකම `attrs["stem"]` සහ `attrs["suffix"]` සකසයි. |

## 2. එයට අවශ්‍ය දේ දක්වන්න {#2-declare-what-it-needs}

Backend එකට වෙනත් පැකේජ හෝ දත්ත අවශ්‍ය නම්, එය class එක තුළ දක්වන්න:

```python
class TransformerNER(Backend):
    extra = "hf"                        # the extra that installs its dependencies
    requires = ("transformers",)        # modules it imports
    resources = ("my-ner-model",)       # resources it downloads on first use
```

එයට අවශ්‍ය පැකේජයක් ස්ථාපනය කර නැති නම්, එය නිවැරදි කිරීමට අවශ්‍ය `pip install` විධානය සමඟ
පරිශීලකයාට දෝෂයක් ලැබේ. පළමු භාවිතයේදී දත්ත ගොනු බාගැනීමට, ඒවා
`sinling.resources.register_resource()` මගින් ලියාපදිංචි කර `sinling.resources.resource_path()`
මගින් විවෘත කරන්න.

## 3. එය ලියාපදිංචි කරන්න {#3-register-it}

ඔබේ පැකේජයේ `pyproject.toml` හි backend එක ගැන Sinling ට කියන්න. නාමය `<task>.<backend>` වේ:

```toml
[project.entry-points."sinling.backends"]
"tokenize.whitespace" = "sinling_whitespace:WhitespaceTokenizer"
```

ප්ලගිනයක් ස්ථාපනය කිරීම Sinling මන්දගාමී නොකරයි: ප්ලගිනය පූරණය වන්නේ යමෙක් එය භාවිත කරන විට
පමණි. කරුණාකර ප්ලගින PyPI හි `sinling-whitespace` වැනි, `sinling-` වලින් ආරම්භ වන නාමයකින්
ප්‍රකාශයට පත් කරන්න.

## 4. එය භාවිත කර ඇගයීම {#4-use-and-evaluate-it}

```python
sinling.tokenize("මම ගෙදර යනවා.", backend="whitespace")
sinling.evaluate("tokenize", "ud-sinhala-stb", backend="whitespace")
```

`sinling.backends("tokenize")` එය ගොඩනැගූ backends අසලින් ලැයිස්තුගත කරයි.
