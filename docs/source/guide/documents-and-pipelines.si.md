# ලේඛන සහ නල මාර්ග

කාර්ය ශ්‍රිත සරල අගයන් ලබා දෙයි; බොහෝ ස්ක්‍රිප්ට් සඳහා එය ප්‍රමාණවත්ය. නල මාර්ගයක් (pipeline)
එක් `Doc` එකක් මත කාර්ය කිහිපයක් ධාවනය කර ඒවා සොයාගන්නා සියල්ල රඳවා ගනී.

```python
>>> import sinling
>>> nlp = sinling.pipeline(["normalize", "tokenize", "sentences"])
>>> doc = nlp("\N{ZERO WIDTH SPACE}මම යනවා. ඔයා එනවා.")

```

පියවර කිසිවක් නොදුන් `sinling.pipeline()` ධාවනය කරන්නේ හරියටම මෙම කාර්ය තුනයි. නල මාර්ගයක්
සෑම backend එකක්ම එක් වරක් පමණක් ගොඩනඟයි; ඒ නිසා බොහෝ පෙළ සඳහා එය නැවත භාවිත කරන්න.

## Doc {#the-doc}

| ගුණාංගය | අඩංගු දේ |
| --- | --- |
| `doc.raw` | දුන් පෙළ හරියටම. එය කිසි විටෙකත් වෙනස් නොවේ. |
| `doc.text` | සාමාන්‍යකරණයෙන් හෝ පැරණි ෆොන්ට හැරවීමෙන් පසු වැඩ කරන පෙළ. |
| `doc.tokens` | `Token` ලැයිස්තුවක්: `text`, `doc.text` තුළ `start` සහ `end` ස්ථාන, සහ `attrs`. |
| `doc.sents` | `Span` ලැයිස්තුවක්: `start` සහ `end` ටෝකන දර්ශක, විකල්ප `label` සහ `score` සමඟ. |
| `doc.spans` | නම් කළ span කාණ්ඩ, උදාහරණයක් ලෙස නාමිත ඒකක සඳහා `doc.spans["ents"]`. |
| `doc.meta` | ලේඛනය පිළිබඳ ප්‍රතිඵල, උදාහරණයක් ලෙස සිතියම් නොකළ පැරණි ෆොන්ට අකුරු. |

```python
>>> doc.text
'මම යනවා. ඔයා එනවා.'
>>> doc.tokens[1]
Token(text='යනවා', start=3, end=7, attrs={'kind': 'word'})
>>> doc.span_text(doc.sents[1])
'ඔයා එනවා.'

```

## මුල් පෙළට ආපසු {#offsets-back-to-the-original}

සාමාන්‍යකරණය සහ පැරණි ෆොන්ට හැරවීම පෙළ වෙනස් කරයි, නමුත් සෑම වෙනසක්ම සටහන් වේ.
`doc.to_raw()` ටෝකනයක්, span එකක් හෝ `doc.text` හි අකුරු පරාසයක් `doc.raw` වෙත සිතියම්ගත
කරයි; ඒ නිසා ප්‍රතිඵලයක් මුල් ලේඛනයේ ඉස්මතු කළ හැකිය:

```python
>>> start, end = doc.to_raw(doc.tokens[1])
>>> (start, end), doc.raw[start:end]
((4, 8), 'යනවා')

```

මෙහි මුල් පෙළ නොපෙනෙන ශුන්‍ය-පළල හිස්තැනකින් ආරම්භ වන නිසා, සෑම ස්ථානයක්ම එකකින් වෙනස් වේ.

## පියවර {#steps}

පියවරක් යනු කාර්ය නාමයක් (එහි පෙරනිමි backend එක), `(task, backend)` හෝ
`(task, backend, options)` tuple එකක්, හෝ `task`, `backend` සහ `config` යතුරු සහිත dict එකකි:

```python
nlp = sinling.pipeline([
    ("legacy_font", "fm"),
    ("normalize", "rules", {"preset": "search"}),
    "tokenize",
    {"task": "stem", "backend": "dictionary"},
])
```

පෙළ වෙනස් කරන පියවර (සාමාන්‍යකරණය, පැරණි ෆොන්ට හැරවීම) අනෙක් සියල්ලට පෙර තිබිය යුතුය;
නල මාර්ගය වෙනත් අනුපිළිවෙළක් ප්‍රතික්ෂේප කරයි. `sentences` සහ `stem` වැනි ටෝකන අවශ්‍ය කාර්ය,
`tokenize` ධාවනය වී නොමැති නම් දෝෂයක් මතු කරයි.

## Doc එකක් සුරැකීම {#saving-a-doc}

`doc.to_dict()` JSON ලෙස ලිවිය හැකි සරල දත්ත ලබා දෙයි; `Doc.from_dict()` සම්බන්ධතාවද
(alignment) ඇතුළුව ලේඛනය නැවත ගොඩනඟයි:

```python
>>> import json
>>> copy = sinling.Doc.from_dict(json.loads(json.dumps(doc.to_dict())))
>>> copy.to_raw(copy.tokens[1])
(4, 8)

```
