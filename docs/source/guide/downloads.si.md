# බාගැනීම් සහ නොබැඳි භාවිතය

පෙළ පිරිසිදු කිරීම, වචන සහ වාක්‍යවලට බෙදීම, සහ පැරණි ෆොන්ට හැරවීම අන්තර්ජාලය නැතිව ක්‍රියා
කරයි. ඔබ පළමු වරට භාවිත කරන විට Sinling බාගන්නා දත්ත අවශ්‍ය වන්නේ අංග කිහිපයකට පමණි. Sinling
සෑම ගොනුවකම සෑම විටම එකම අනුවාදය බාගන්නා අතර, එය නිවැරදිව ලැබුණු බව පරීක්ෂා කරයි. ගොනු
`~/.cache/sinling` හි සුරැකේ.

## බාගැනීමක් අවශ්‍ය දේ {#what-needs-a-download}

| බාගැනීම | ප්‍රමාණය | අවශ්‍ය වන්නේ | මූලාශ්‍රය |
| --- | --- | --- | --- |
| `sinhala-suffixes` | 6 KB | `stem()` | sinhala-stemmer ව්‍යාපෘතිය (බලපත්‍රයක් නැත) |
| `sinhala-stem-dictionary` | 1.3 MB | `stem(..., backend="dictionary")` | sinhala-stemmer ව්‍යාපෘතිය (බලපත්‍රයක් නැත) |
| `ud-sinhala-stb` | 112 KB | `evaluate()` | Universal Dependencies (CC BY-SA 4.0) |
| `ud-sinhala-appuwa` | 86 KB | `evaluate()` | Universal Dependencies (CC BY-SA 4.0) |

Python වලින් පරීක්ෂා කිරීමට, කාර්යයක් කරන සෑම ක්‍රමයක්ම බාගන්නා දේ `sinling.backends()`
ලැයිස්තුගත කරයි:

```python
>>> import sinling
>>> {(b.task, b.name): b.downloads for b in sinling.backends()}["stem", "dictionary"]
('sinhala-suffixes', 'sinhala-stem-dictionary')

```

## සැකසුම් {#settings}

| පරිසර විචල්‍යය | කරන දේ |
| --- | --- |
| `SINLING_HOME` | `~/.cache/sinling` වෙනුවට බාගැනීම් මෙම ෆෝල්ඩරයේ සුරකියි. |
| `SINLING_OFFLINE=1` | කිසි විටෙකත් බාගන්නේ නැත. ගොනුවක් නැති නම්, එය ලබා ගන්නා ආකාරය දෝෂ පණිවිඩය කියයි. |

## අන්තර්ජාලය නැතිව Sinling භාවිත කිරීම {#using-sinling-without-internet}

අන්තර්ජාලය ඇති පරිගණකයක ඔබට අවශ්‍ය දේ බාගන්න:

```python
import sinling
sinling.download("sinhala-suffixes")
sinling.download("sinhala-stem-dictionary")
```

ඉන්පසු `~/.cache/sinling` ෆෝල්ඩරය අන්තර්ජාලය නැති පරිගණකයට පිටපත් කරන්න. එහි
`SINLING_OFFLINE=1` සැකසීමෙන් Sinling කිසි විටෙකත් සම්බන්ධ වීමට උත්සාහ නොකරන බව සහතික වේ.
