# Evaluation

Every backend is scored on public test sets, so you can see how well it works before relying on
it, and compare backends on your own data.

## Current results

The default backends on the two [Universal Dependencies](https://universaldependencies.org/)
Sinhala treebanks (release 2.18):

| Task | Backend | Dataset | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- |
| tokenize | rules | UD Sinhala STB (100 sentences) | 1.000 | 1.000 | 1.000 |
| tokenize | rules | UD Sinhala Appuwa (69 sentences) | 0.994 | 0.997 | 0.996 |
| sentences | rules | UD Sinhala STB | 1.000 | 1.000 | 1.000 |
| sentences | rules | UD Sinhala Appuwa | 0.958 | 1.000 | 0.979 |

Most of the remaining differences are annotation choices in Appuwa: two tokens keep their
punctuation attached (`නැහැ,`), and three sentences contain a full stop inside them. The test
sets are small, so treat these numbers as a check, not a ranking.

## How it's measured

- The treebanks put a space around every punctuation mark, so their text is **detokenized**
  first: `. , ? ! : ;` and closing brackets are joined to the word before them, and opening
  brackets to the word after. Pass `text="given"` to score on the text as written in the file.
- **Tokens** are scored by their exact character spans: a token counts only if both its start
  and end match.
- **Sentences** are scored by where they end, after joining the treebank's sentences into one
  text.
- The whole pipeline runs (normalization included), and results are mapped back to the
  original text, so normalization can't skew the comparison.

## Running it

```
python -m sinling evaluate
python -m sinling evaluate --task tokenize --dataset my-test-set.conllu --backend rules
```

```python
report = sinling.evaluate("sentences", "ud-sinhala-appuwa")
report.precision, report.recall, report.f1
report.counts  # sentences, skipped, gold, predicted, correct
```

`evaluate()` accepts a registered dataset name or the path to any CoNLL-U file whose sentences
have a `# text =` comment. Backend options are passed through, e.g.
`evaluate("tokenize", "ud-sinhala-stb", extra_abbreviations=["ඩො."])`.

## Datasets

| Name | Sentences | Licence |
| --- | --- | --- |
| `ud-sinhala-stb` | 100 sentences of news, fiction, government and web text | CC BY-SA 4.0 |
| `ud-sinhala-appuwa` | 69 sentences of the folk story "Appuwa" | CC BY-SA 4.0 |

Both are downloaded on first use. If you report results on them, cite Liyanage, Sarveswaran
et al. (2023), *Sinhala Dependency Treebank (STB)*, Proceedings of UDW 2023, and the UD Sinhala
Appuwa treebank.
