# බාගැනීම් සහ නොබැඳි භාවිතය

සාමාන්‍යකරණය, ටෝකනීකරණය, වාක්‍ය වෙන් කිරීම සහ පැරණි ෆොන්ට හැරවීම කිසිදු බාගැනීමක් නොමැතිව
ක්‍රියා කරයි. ප්‍රකෘති සෙවීම වැනි දත්ත අවශ්‍ය backends පළමු භාවිතයේදී එම දත්ත බාගනී.

සෑම බාගැනීමක්ම අනුවාදයකට සවි කර SHA-256 checksum එකකට එරෙහිව පරීක්ෂා කෙරේ; ඒ නිසා දත්ත
නිහඬව වෙනස් විය නොහැක. ගොනු `~/.cache/sinling/<name>/<version>/` හි ගබඩා වේ.

## බාගැනීමක් අවශ්‍ය දේ {#what-needs-a-download}

`sinling.backends()` සෑම backend එකකම බාගැනීම් ලැයිස්තුගත කරයි; හිස් tuple එකක් යනු එය මුල සිටම
අන්තර්ජාලය නැතිව ක්‍රියා කරන බවයි:

```python
>>> import sinling
>>> {(b.task, b.name): b.downloads for b in sinling.backends()}["stem", "dictionary"]
('sinhala-suffixes', 'sinhala-stem-dictionary')

```

| බාගැනීම | ප්‍රමාණය | භාවිත කරන්නේ | මූලාශ්‍රය |
| --- | --- | --- | --- |
| `sinhala-suffixes` | 6 KB | `stem` (`suffix`, `dictionary`) | rksk/sinhala-news-analysis, බලපත්‍රයක් නැත |
| `sinhala-stem-dictionary` | 1.3 MB | `stem` (`dictionary`) | rksk/sinhala-news-analysis, බලපත්‍රයක් නැත |
| `ud-sinhala-stb` | 112 KB | `evaluate()` | Universal Dependencies 2.18, CC BY-SA 4.0 |
| `ud-sinhala-appuwa` | 86 KB | `evaluate()` | Universal Dependencies 2.18, CC BY-SA 4.0 |

## සැකසුම් {#settings}

| පරිසර විචල්‍යය | බලපෑම |
| --- | --- |
| `SINLING_HOME` | `~/.cache/sinling` වෙනුවට මෙම ෆෝල්ඩරය cache එක ලෙස භාවිත කරයි. |
| `SINLING_OFFLINE=1` | කිසි විටෙකත් බාගන්නේ නැත. ගොනුවක් නැති නම්, එය ලබාගැනීමේ විධානය සමඟ `ResourceUnavailableError` මතු කරයි. |

## අන්තර්ජාලය නැති පරිගණකයක් සූදානම් කිරීම {#preparing-a-machine-without-internet}

අන්තර්ජාලයට සම්බන්ධ පරිගණකයක ඔබට අවශ්‍ය දේ බාගෙන, cache ෆෝල්ඩරය පිටපත් කරන්න:

```python
import sinling
sinling.download("sinhala-suffixes")
sinling.download("sinhala-stem-dictionary")
```

කිසිවක් සම්බන්ධ වීමට උත්සාහ නොකරන බව සහතික කිරීමට, අන්තර්ජාලය නැති පරිගණකයේ
`SINLING_OFFLINE=1` සකසන්න.
