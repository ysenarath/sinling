# Sinling

Sinling යනු සිංහල භාෂාව සැකසීම සඳහා වූ මෙවලම් කට්ටලයකි. එය සිංහල පෙළ පිරිසිදු කරයි, ටෝකන
(tokens) හා වාක්‍යවලට වෙන් කරයි, පදවල ප්‍රකෘතිය සොයයි, පැරණි ෆොන්ට (legacy fonts) වලින් ලියූ පෙළ
යුනිකේත (Unicode) බවට හරවයි, සහ මේ එක් එක් කාර්යය පොදු පරීක්ෂණ දත්ත මත කෙතරම් හොඳින් ක්‍රියා
කරනවාද යන්න මනියි.

!!! warning "Sinling 0.4 තවමත් පෙර-නිකුතුවකි"
    0.4 යනු නැවත සැලසුම් කළ අනුවාදයකි; එය 0.3 සමඟ නොගැළපේ. සාමාන්‍ය `pip install sinling`
    විධානය තවමත් 0.3 ස්ථාපනය කරයි. ඔබේ කේතය 0.3 API භාවිත කරන්නේ නම්, `sinling<0.4` ලෙස
    අනුවාදය සවි කරන්න. [මාරු වීමේ මාර්ගෝපදේශය](migration.md) පැරණි API නව API වෙත සිතියම්ගත
    කරයි.

## ස්ථාපනය {#installation}

```
pip install --pre sinling
```

Sinling 0.4 සඳහා Python 3.11 හෝ ඊට නවතම අනුවාදයක් අවශ්‍යයි. වෙනත් පැකේජ කිසිවක් අවශ්‍ය නැත.

## ඉක්මන් ආරම්භය {#quick-start}

සෑම කාර්යයක්ම පෙළ ලබාගෙන සරල Python අගයන් ලබා දෙන එක් ශ්‍රිතයකි:

```python
>>> import sinling

>>> sinling.normalize("\N{SINHALA VOWEL SIGN KOMBUVA}ගදර\N{NO-BREAK SPACE}යනවා")
'ගෙදර යනවා'

>>> sinling.tokenize("පෙ.ව. 10ට රු.500ක් ගෙවන්න.")
['පෙ.ව.', '10ට', 'රු.', '500ක්', 'ගෙවන්න', '.']

>>> sinling.sentences("මම ගෙදර යනවා. ඔයා එනවද?")
['මම ගෙදර යනවා.', 'ඔයා එනවද?']

```

සියල්ල එකවර අවශ්‍ය නම්, නල මාර්ගයක් (pipeline) `Doc` එකක් ලබා දෙයි. එහි ටෝකන, වාක්‍ය සහ මුල්
පෙළට ආපසු යන සම්බන්ධතාව (alignment) රැඳේ:

```python
>>> doc = sinling.pipeline()("මම ගෙදර යනවා. ඔයා එනවද?")
>>> [token.text for token in doc.tokens]
['මම', 'ගෙදර', 'යනවා', '.', 'ඔයා', 'එනවද', '?']
>>> len(doc.sents)
2

```

## අන්තර්ගතය {#whats-included}

| කාර්යය | ශ්‍රිතය | Backends | බාගැනීම් |
| --- | --- | --- | --- |
| [සාමාන්‍යකරණය](guide/normalization.md) | `normalize()` | `rules` | නැත |
| [ටෝකනීකරණය](guide/tokens-and-sentences.md) | `tokenize()` | `rules` | නැත |
| [වාක්‍ය වෙන් කිරීම](guide/tokens-and-sentences.md) | `sentences()` | `rules` | නැත |
| [ප්‍රකෘතිය සෙවීම](guide/stemming.md) | `stem()` | `suffix`, `dictionary` | ප්‍රත්‍යය ලැයිස්තුව, ප්‍රකෘති ශබ්දකෝෂය |
| [පැරණි ෆොන්ට](guide/legacy-fonts.md) | `from_legacy_font()` | `fm` | නැත |
| [අක්ෂරවලට බෙදීම](guide/normalization.md#aksharas) | `aksharas()` | — | නැත |

සෑම කාර්ය ශ්‍රිතයකටම එකම හැඩයක් ඇත: මුලින්ම පෙළ, ඉන්පසු නමින් පමණක් දිය හැකි `backend=`,
`normalize=` සහ backend විකල්ප. Backend යනු කාර්යයක් ඉටු කරන එක් ක්‍රමයකි; වෙනත් පැකේජවලට
[ප්ලගින](guide/plugins.md) ලෙස අලුත් backends එක් කළ හැකිය. පොදු පරීක්ෂණ දත්ත මත නිරවද්‍යතාව
[ඇගයීම](guide/evaluation.md) පිටුවේ ඇත.

## බලපත්‍රය {#license}

Apache License 2.0.
