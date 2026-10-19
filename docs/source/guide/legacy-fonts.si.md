# පැරණි සිංහල ෆොන්ට

යුනිකේත පැමිණීමට පෙර සිංහල ටයිප් කළේ ඉංග්‍රීසි අකුරු වෙනුවට සිංහල අකුරු පෙන්වන ෆොන්ටවලිනි.
එවැනි ෆොන්ට එකක් භාවිත කරන PDF හෝ Word ගොනුවකින් පෙළ පිටපත් කළ විට, `වාතය` වෙනුවට `jd;h`
වැනි තේරුමක් නැති අකුරු ලැබේ. බොහෝ රජයේ ලේඛන සහ පාසල් පෙළපොත් තවමත් ඒවා භාවිත කරයි.

`from_legacy_font()` එම පෙළ නිවැරදි යුනිකේත සිංහල බවට හරවා පිරිසිදු කරයි:

```python
>>> import sinling
>>> sinling.from_legacy_font('jd;h" c,h" wdydr')
'වාතය, ජලය, ආහාර'

>>> sinling.from_legacy_font("fomd\xbe;f\xefka;=j")
'දෙපාර්තමේන්තුව'

```

## සහාය දක්වන ෆොන්ට {#supported-fonts}

| `backend=` | ෆොන්ට |
| --- | --- |
| `fm` (පෙරනිමිය) | FM ෆොන්ට: FMAbhaya, FMMalithi, FMEmanee, FMAbabld සහ එකම විජේසේකර යතුරුපුවරු පිරිසැලසුම ඇති අනෙක් ෆොන්ට. |

DL ෆොන්ට සහ Bamini වැනි පැරණි දෙමළ ෆොන්ට සඳහා සහාය සැලසුම් කර ඇත. FM හැරවීම පාසල් පෙළපොත්
31 කින් ලබාගත් අකුරු මිලියන 2.8 ක් මත පරීක්ෂා කර ඇත.

## පැරණි ෆොන්ට එකක ඇති පෙළ පමණක් හරවන්න {#convert-only-text-in-an-old-font}

හරවන්නා ඉංග්‍රීසි අකුරු සහ විරාම ලකුණු සිංහල බවට හරවන නිසා, සාමාන්‍ය ඉංග්‍රීසි පෙළ විනාශ වේ.
දැනටමත් යුනිකේත සිංහලෙන් ඇති පෙළ නොවෙනස්ව පවතී.

PDF එකක, FM ෆොන්ට එකකින් ටයිප් කළ කොටස් පමණක් හරවන්න. ෆොන්ට නාමයක් ඒවායින් එකක්දැයි
`is_fm_font()` කියයි; PDF භාවිත කරන `ABCDEF+FMAbhaya` වැනි නාම සහ නම "FM" වලින් ආරම්භ නොවන
FM ෆොන්ට තුනද ඇතුළුව:

```python
>>> from sinling.legacy_fonts import is_fm_font
>>> is_fm_font("ABCDEF+FMAbhaya"), is_fm_font("SARAWIPULA"), is_fm_font("Iskoola Pota")
(True, True, False)

```

## හරවන්නා නොදන්නා අකුරු {#characters-it-doesnt-know}

හරවන්නා නොදන්නා අකුරු එලෙසම තබා `doc.meta["legacy_font_unmapped"]` හි ගණන් කෙරේ; එවිට අඩුව
ඇත්තේ කුමක්දැයි ඔබට දැකිය හැකිය:

```python
>>> doc = sinling.pipeline(["legacy_font"])("jd;h\N{EURO SIGN}")
>>> doc.text, doc.meta["legacy_font_unmapped"]
('වාතය€', {'€': 1})

```

ෆොන්ට එක සමහර ස්වර ලකුණු අකුරට පෙර ගබඩා කළත්, හැරවූ සෑම අකුරක්ම මුල් පෙළේ කොතැනින්
පැමිණියේදැයි ඔබට සොයා ගත හැකිය:

```python
>>> doc = sinling.pipeline(["legacy_font"])("frda.")
>>> doc.text, doc.raw[slice(*doc.to_raw(0, 2))]
('රෝග', 'frda')

```
