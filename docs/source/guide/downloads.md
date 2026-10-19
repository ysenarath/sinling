# Downloads and offline use

Normalization, tokenization, sentence splitting and legacy-font conversion work without any
download. Backends that need data, such as the stemmers, download it on first use.

Every download is pinned to a version and checked against a SHA-256 checksum, so the data can't
change silently. Files are cached in `~/.cache/sinling/<name>/<version>/`.

## What needs a download

`sinling.backends()` lists each backend's downloads; an empty tuple means it works offline from
the start:

```python
>>> import sinling
>>> {(b.task, b.name): b.downloads for b in sinling.backends()}["stem", "dictionary"]
('sinhala-suffixes', 'sinhala-stem-dictionary')

```

| Download | Size | Used by | Source |
| --- | --- | --- | --- |
| `sinhala-suffixes` | 6 KB | `stem` (`suffix`, `dictionary`) | rksk/sinhala-news-analysis, no licence |
| `sinhala-stem-dictionary` | 1.3 MB | `stem` (`dictionary`) | rksk/sinhala-news-analysis, no licence |
| `ud-sinhala-stb` | 112 KB | `evaluate()` | Universal Dependencies 2.18, CC BY-SA 4.0 |
| `ud-sinhala-appuwa` | 86 KB | `evaluate()` | Universal Dependencies 2.18, CC BY-SA 4.0 |

## Settings

| Environment variable | Effect |
| --- | --- |
| `SINLING_HOME` | Use this directory for the cache instead of `~/.cache/sinling`. |
| `SINLING_OFFLINE=1` | Never download. A missing file raises `ResourceUnavailableError` with the command to fetch it. |

## Preparing a machine without internet

On a connected machine, download what you need, then copy the cache directory over:

```python
import sinling
sinling.download("sinhala-suffixes")
sinling.download("sinhala-stem-dictionary")
```

Set `SINLING_OFFLINE=1` on the offline machine to make sure nothing tries to connect.
