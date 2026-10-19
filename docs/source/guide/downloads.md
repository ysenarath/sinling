# Downloads and offline use

Cleaning up text, splitting it into words and sentences, and converting old fonts all work
without the internet. A few features need data that Sinling downloads the first time you use
them. Sinling always downloads the same version of each file and checks that it arrived intact.
Files are saved in `~/.cache/sinling`.

## What needs a download

| Download | Size | Needed for | Comes from |
| --- | --- | --- | --- |
| `sinhala-suffixes` | 6 KB | `stem()` | the sinhala-stemmer project (no licence) |
| `sinhala-stem-dictionary` | 1.3 MB | `stem(..., backend="dictionary")` | the sinhala-stemmer project (no licence) |
| `ud-sinhala-stb` | 112 KB | `evaluate()` | Universal Dependencies (CC BY-SA 4.0) |
| `ud-sinhala-appuwa` | 86 KB | `evaluate()` | Universal Dependencies (CC BY-SA 4.0) |

To check from Python, `sinling.backends()` lists what each way of doing a task downloads:

```python
>>> import sinling
>>> {(b.task, b.name): b.downloads for b in sinling.backends()}["stem", "dictionary"]
('sinhala-suffixes', 'sinhala-stem-dictionary')

```

## Settings

| Environment variable | What it does |
| --- | --- |
| `SINLING_HOME` | Saves downloads in this folder instead of `~/.cache/sinling`. |
| `SINLING_OFFLINE=1` | Never downloads. If a file is missing, the error tells you how to get it. |

## Using Sinling without internet

On a computer with internet, download what you need:

```python
import sinling
sinling.download("sinhala-suffixes")
sinling.download("sinhala-stem-dictionary")
```

Then copy the `~/.cache/sinling` folder to the offline computer. Setting `SINLING_OFFLINE=1`
there makes sure Sinling never tries to connect.
