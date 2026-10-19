# Evaluation

How accurate is Sinling? Each feature is tested on publicly available Sinhala text that people
have checked by hand. You can run the same tests yourself, and on your own data.

## Results

Tested on the two Sinhala treebanks of [Universal Dependencies](https://universaldependencies.org/),
collections of sentences split into words by hand:

| Task | Test data | Precision | Recall | F1 |
| --- | --- | --- | --- | --- |
| Splitting into words | UD Sinhala STB (100 sentences) | 1.000 | 1.000 | 1.000 |
| Splitting into words | UD Sinhala Appuwa (69 sentences) | 0.994 | 0.997 | 0.996 |
| Splitting into sentences | UD Sinhala STB | 1.000 | 1.000 | 1.000 |
| Splitting into sentences | UD Sinhala Appuwa | 0.958 | 1.000 | 0.979 |

Precision is the share of Sinling's answers that are right, recall is the share of the right
answers Sinling found, and F1 combines the two; 1.000 is perfect.

Most of the remaining differences come from how the Appuwa sentences were marked up: two words
keep a comma or full stop attached (`නැහැ,`), and three of its sentences contain a full stop
inside them, where Sinling starts a new sentence. The test sets are small, so treat these
numbers as a check rather than a precise measure.

## How the tests work

- The test files put a space before every punctuation mark (`ගියා .`). Sinling removes those
  spaces first, so it sees text as people write it. Pass `text="given"` to test on the text
  exactly as in the file.
- A word counts as right only if Sinling splits it at exactly the same place.
- A sentence counts as right if it ends at the same place.
- The text goes through the same steps as in normal use, including `normalize()`.

## Running the tests

From the command line:

```
python -m sinling evaluate
python -m sinling evaluate --task tokenize --dataset my-test-set.conllu
```

From Python:

```python
report = sinling.evaluate("sentences", "ud-sinhala-appuwa")
report.precision, report.recall, report.f1
```

To test on your own data, give the path to a CoNLL-U file, the format Universal Dependencies
uses; each sentence needs a `# text =` line. You can pass the same options as to the task
itself, e.g. `evaluate("tokenize", "ud-sinhala-stb", extra_abbreviations=["ඩො."])`.

## Test data

| Name | What it contains | Licence |
| --- | --- | --- |
| `ud-sinhala-stb` | 100 sentences of news, stories, government and web text | CC BY-SA 4.0 |
| `ud-sinhala-appuwa` | 69 sentences of the folk story "Appuwa" | CC BY-SA 4.0 |

Both are downloaded the first time you run a test. If you publish results on them, please cite
Liyanage, Sarveswaran et al. (2023), *Sinhala Dependency Treebank (STB)*, Proceedings of UDW
2023, and the UD Sinhala Appuwa treebank.
