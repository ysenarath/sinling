# ඇගයීම

සෑම backend එකක්ම පොදු පරීක්ෂණ දත්ත මත ලකුණු කෙරේ. එවිට එය මත විශ්වාසය තැබීමට පෙර එය කෙතරම්
හොඳින් ක්‍රියා කරනවාද යන්න දැක, ඔබේම දත්ත මත backends සංසන්දනය කළ හැකිය.

## වර්තමාන ප්‍රතිඵල {#current-results}

[Universal Dependencies](https://universaldependencies.org/) සිංහල වාක්‍ය-ගස් බැංකු (treebanks)
දෙක මත (2.18 නිකුතුව) පෙරනිමි backends:

| කාර්යය | Backend | දත්ත කට්ටලය | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- |
| tokenize | rules | UD Sinhala STB (වාක්‍ය 100) | 1.000 | 1.000 | 1.000 |
| tokenize | rules | UD Sinhala Appuwa (වාක්‍ය 69) | 0.994 | 0.997 | 0.996 |
| sentences | rules | UD Sinhala STB | 1.000 | 1.000 | 1.000 |
| sentences | rules | UD Sinhala Appuwa | 0.958 | 1.000 | 0.979 |

ඉතිරි වෙනස්කම්වලින් වැඩි හරියක් Appuwa හි ව්‍යාඛ්‍යාන (annotation) තීරණය: ටෝකන දෙකක් තම විරාම
ලකුණ ඇලවී තබා ගනී (`නැහැ,`), සහ වාක්‍ය තුනක් තුළ තිතක් ඇත. පරීක්ෂණ දත්ත කුඩා නිසා, මෙම
අංක ශ්‍රේණිගත කිරීමක් ලෙස නොව පරීක්ෂාවක් ලෙස සලකන්න.

## මනින ආකාරය {#how-its-measured}

- වාක්‍ය-ගස් බැංකු සෑම විරාම ලකුණක් වටාම හිස්තැනක් තබයි; ඒ නිසා ඒවායේ පෙළ මුලින්ම
  **ටෝකන-ඉවත් (detokenized)** කෙරේ: `. , ? ! : ;` සහ වසන වරහන් පෙර වචනයට ද, විවෘත වරහන්
  ඊළඟ වචනයට ද එක් කෙරේ. ගොනුවේ ලියා ඇති පරිදිම පෙළ මත ලකුණු කිරීමට `text="given"` දෙන්න.
- **ටෝකන** ලකුණු කරන්නේ ඒවායේ නිවැරදි අකුරු පරාසයෙනි: ටෝකනයක් ගණන් ගන්නේ එහි ආරම්භය සහ
  අවසානය දෙකම ගැළපේ නම් පමණි.
- **වාක්‍ය** ලකුණු කරන්නේ, වාක්‍ය-ගස් බැංකුවේ වාක්‍ය එක් පෙළකට එකතු කළ පසු, ඒවා අවසන් වන
  තැනෙනි.
- සම්පූර්ණ නල මාර්ගය (සාමාන්‍යකරණය ද ඇතුළුව) ධාවනය වී, ප්‍රතිඵල මුල් පෙළට ආපසු සිතියම්ගත
  කෙරේ; ඒ නිසා සාමාන්‍යකරණය සංසන්දනයට බලපාන්නේ නැත.

## ධාවනය කිරීම {#running-it}

```
python -m sinling evaluate
python -m sinling evaluate --task tokenize --dataset my-test-set.conllu --backend rules
```

```python
report = sinling.evaluate("sentences", "ud-sinhala-appuwa")
report.precision, report.recall, report.f1
report.counts  # sentences, skipped, gold, predicted, correct
```

`evaluate()` ලියාපදිංචි දත්ත කට්ටල නාමයක් හෝ, වාක්‍යවලට `# text =` සටහනක් ඇති ඕනෑම CoNLL-U
ගොනුවක මාර්ගයක් පිළිගනී. Backend විකල්ප ඒ හරහා යවනු ලැබේ, උදාහරණයක් ලෙස
`evaluate("tokenize", "ud-sinhala-stb", extra_abbreviations=["ඩො."])`.

## දත්ත කට්ටල {#datasets}

| නාමය | වාක්‍ය | බලපත්‍රය |
| --- | --- | --- |
| `ud-sinhala-stb` | ප්‍රවෘත්ති, ප්‍රබන්ධ, රජයේ සහ වෙබ් පෙළ වාක්‍ය 100 | CC BY-SA 4.0 |
| `ud-sinhala-appuwa` | "අප්පුවා" ජනකතාවේ වාක්‍ය 69 | CC BY-SA 4.0 |

දෙකම පළමු භාවිතයේදී බාගනු ලැබේ. ඒවා මත ප්‍රතිඵල වාර්තා කරන්නේ නම්, Liyanage, Sarveswaran
et al. (2023), *Sinhala Dependency Treebank (STB)*, Proceedings of UDW 2023, සහ UD Sinhala
Appuwa වාක්‍ය-ගස් බැංකුව උපුටා දක්වන්න.
