# Does extra knowledge help LLMs translate English into Sinhala?

This experiment tests whether a cheap LLM translates English into Sinhala better when it gets
help, and which kind of help matters. Each model translates the same 1,012 sentences five ways:

| Setup | What the model gets |
| --- | --- |
| `base` | The English sentence only. |
| `glossary` | Plus Sinhala translations of names and terms found in the sentence. |
| `examples` | Plus four similar sentences with their human translations. |
| `both` | Plus the glossary and the examples. |
| `review` | Like `both`, then the translation is checked and revised up to twice. |

In `review`, two kinds of checks look at each translation. Automatic checks catch missing
numbers, words left in English, glossary terms that weren't used, and translations that are far
too short or long. Then the model reviews the translation against a short Sinhala grammar
checklist. Any problems are sent back to the model to fix, and the version with the fewest
problems is kept.

## Data

| Data | Used for | Licence |
| --- | --- | --- |
| [FLORES-200](https://github.com/facebookresearch/flores) `devtest` | the 1,012 test sentences and their human translations | CC BY-SA 4.0 |
| FLORES-200 `dev` | the pool of example sentences (never the test sentences) | CC BY-SA 4.0 |
| [Wikidata](https://www.wikidata.org/) labels | glossary: names, places, organisations, concepts | CC0 |
| [Wiktionary](https://en.wiktionary.org/), via [kaikki.org](https://kaikki.org/) | glossary: general words | CC BY-SA 4.0 |

All data, model outputs and cached responses are kept in `data/`, which is not committed.

## Scoring

Translations are scored with chrF++ against the human translations, after cleaning up both sides
with `sinling.normalize()`. chrF++ compares character sequences, which suits Sinhala because
words change their endings. Higher is better.

## Running it

You need [uv](https://docs.astral.sh/uv/), an OpenRouter API key in `OPENROUTER_API_KEY`, and the
Sinling wheel built into `dist/` at the top of the repository (`uv build --out-dir dist`).

```
python3 scripts/prepare_flores.py              # after downloading the FLORES-200 archive into data/flores/
python3 scripts/build_wikidata_glossary.py
curl -sL https://kaikki.org/dictionary/English/kaikki.org-dictionary-English.jsonl \
    | python3 scripts/extract_wiktionary.py data/glossary/wiktionary_en_si.jsonl

./run.sh translate.py deepseek/deepseek-v4.1-flash base
./run.sh translate.py deepseek/deepseek-v4.1-flash review --limit 50
./run.sh score.py
```

Every response is cached, so running a step again costs nothing. The total spend is kept in
`data/spend.json`, and no request is sent once it reaches the cap ($5 by default; set
`TRANSLATION_BUDGET_USD` to change it). Requests run several at a time, so the cap can be passed
by a few requests.

The models are told not to use hidden reasoning, and requests only go to OpenRouter providers that
honour that setting. Without it, some responses spent their whole token allowance thinking and came
back empty.

## Results

Run on 2026-10-19: all 1,012 FLORES-200 devtest sentences, temperature 0, chrF++ after
`sinling.normalize()`. Each difference compares the same sentences, with a 95% interval from 1,000
bootstrap resamples. Total cost: $1.29.

| Model | Plain prompt | + glossary | + examples | + both |
| --- | --- | --- | --- | --- |
| DeepSeek v4.1 Flash | 49.4 | −0.2 (−0.4 to +0.1) | **+0.7** (+0.2 to +1.1) | +0.4 (−0.1 to +0.8) |
| Gemini 2.5 Flash-Lite | 46.9 | −0.1 (−0.4 to +0.1) | **+2.0** (+1.4 to +2.7) | +1.8 (+1.2 to +2.4) |
| Qwen 3.7 Flash | 39.8 | +0.1 (−0.1 to +0.4) | **+2.1** (+1.6 to +2.5) | +1.8 (+1.4 to +2.3) |

Revising after checks, on DeepSeek, compared with `both` (its starting point):

| Setup | Change | Sentences revised | Cost for 1,012 sentences |
| --- | --- | --- | --- |
| `both` | — | — | $0.22 |
| `checks`: automatic checks only | −0.0 (−0.4 to +0.3) | 34 | $0.24 |
| `review`: checks plus the model's own grammar review | −0.3 (−0.7 to +0.1) | 366 | $0.78 |

What this shows:

- **Similar example sentences help every model.** The weaker the model, the bigger the gain: about
  +2 points for Gemini Flash-Lite and Qwen, +0.7 for DeepSeek.
- **A glossary from Wikidata and Wiktionary makes no difference on this text.** FLORES is general
  news, and the models already know these names and words: on the first 50 sentences, the plain
  translation already used the glossary's form as often as the human translators did. Where the
  glossary differed, it was usually an equally valid spelling or a formal official name (India →
  භාරත ජනරජය instead of ඉන්දියාව). A glossary is more likely to matter for specialised text, where one
  exact term is required; FLORES doesn't test that.
- **The automatic checks rarely fire** (44 of 1,012 sentences) and change nothing measurable.
- **A cheap model reviewing its own work doesn't help.** It flagged half the sentences, often with
  problems that weren't real, and its revisions scored slightly lower at 3.5 times the cost.

Limits of this experiment:

- chrF++ against a single human translation; no COMET or human judgement, so a valid alternative
  wording counts as an error.
- One general-domain test set, three cheap models, one run each.
- The glossary filter and two checks were adjusted after looking at the first 50 test sentences.
  That could only have flattered the glossary and the checks, and they still showed no gain, but
  it is not a clean held-out design.

For Sinling's `translate()`: retrieving similar translated examples is worth building. A glossary
should be something users supply for their own domain, not filled automatically from Wikidata. The
review loop should be off by default; whether a stronger reviewer model helps is untested.
