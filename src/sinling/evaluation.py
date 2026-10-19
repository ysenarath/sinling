"""Score a task's backend on a public test set: ``sinling.evaluate(task, dataset)``.

Datasets are downloaded on first use, like other resources, and are never shipped with Sinling.
Run ``python -m sinling evaluate`` to print the accuracy table in the README.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sinling.doc import Doc
from sinling.registry import get_backend
from sinling.resources import Resource, register_resource, resource_path

__all__ = ['Dataset', 'Report', 'Sentence', 'accuracy_table', 'datasets', 'detokenize', 'evaluate', 'read_conllu', 'register_dataset']

TASKS = ('tokenize', 'sentences')


@dataclass(frozen=True)
class Dataset:
    """A test set in CoNLL-U format, stored as a downloadable resource."""

    name: str
    resource: str
    license: str
    homepage: str
    citation: str
    tasks: tuple[str, ...] = TASKS


@dataclass(frozen=True)
class Sentence:
    text: str
    tokens: list[str]  # surface tokens (a multiword token counts once)
    lemmas: list[str] = field(default_factory=list)
    upos: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Report:
    """The scores of one backend on one dataset."""

    task: str
    backend: str
    dataset: str
    precision: float
    recall: float
    f1: float
    counts: dict[str, int]

    def __str__(self) -> str:
        return (f'{self.task} [{self.backend}] on {self.dataset}: precision {self.precision:.3f}, '
                f'recall {self.recall:.3f}, F1 {self.f1:.3f} ({self.counts["sentences"]} sentences)')

    def to_dict(self) -> dict[str, Any]:
        return {'task': self.task, 'backend': self.backend, 'dataset': self.dataset, 'precision': self.precision,
                'recall': self.recall, 'f1': self.f1, 'counts': dict(self.counts)}


_datasets: dict[str, Dataset] = {}


def register_dataset(dataset: Dataset) -> Dataset:
    _datasets[dataset.name] = dataset
    return dataset


def datasets() -> list[Dataset]:
    return sorted(_datasets.values(), key=lambda d: d.name)


def _ud(name: str, repo: str, file: str, commit: str, sha256: str, size: int, citation: str) -> None:
    register_resource(Resource(
        name, '2.18', f'https://raw.githubusercontent.com/UniversalDependencies/{repo}/{commit}/{file}',
        sha256, size=size, license='CC-BY-SA-4.0', description=f'Universal Dependencies {repo}, release 2.18'))
    register_dataset(Dataset(name, name, 'CC BY-SA 4.0',
                             f'https://github.com/UniversalDependencies/{repo}', citation))


_ud('ud-sinhala-stb', 'UD_Sinhala-STB', 'si_stb-ud-test.conllu', '2ff193a7039e397ceb109127e9633c1225c2c933',
    '7847eb43b4199aab75d84b4f63d2009e7d8ca47600e90bc5a2df60071798e3b6', 112199,
    'Liyanage, Sarveswaran et al. (2023). Sinhala Dependency Treebank (STB). Proceedings of UDW 2023.')
_ud('ud-sinhala-appuwa', 'UD_Sinhala-Appuwa', 'si_appuwa-ud-test.conllu', '103ce6495c7ccbb53e33063346da15ba964f0555',
    'a9da717514c50331aa01039a4fe926c8dc93b14203bee450a4749429120b21bb', 85973,
    'UD Sinhala Appuwa treebank, Universal Dependencies 2.18.')


def read_conllu(path: str | Path) -> list[Sentence]:
    """Read sentences from a CoNLL-U file; each needs a ``# text =`` comment."""
    sentences = []
    for block in Path(path).read_text(encoding='utf-8').strip().split('\n\n'):
        text, tokens, lemmas, upos, covered_until = None, [], [], [], 0
        for line in block.split('\n'):
            if line.startswith('# text = '):
                text = line[len('# text = '):]
            if not line or line.startswith('#'):
                continue
            cols = line.split('\t')
            if '-' in cols[0]:  # a multiword token: one surface token covering several words
                tokens.append(cols[1])
                covered_until = int(cols[0].split('-')[1])
            elif '.' not in cols[0]:  # skip empty nodes
                if int(cols[0]) > covered_until:
                    tokens.append(cols[1])
                lemmas.append(cols[2])
                upos.append(cols[3])
        if text is None:
            raise ValueError(f'{path}: a sentence has no "# text =" comment')
        sentences.append(Sentence(text, tokens, lemmas, upos))
    return sentences


_SPACE_BEFORE = re.compile(r' (?=[.,?!:;)\]}\N{RIGHT DOUBLE QUOTATION MARK}\N{RIGHT SINGLE QUOTATION MARK}])')
_SPACE_AFTER = re.compile(r'(?<=[(\[{\N{LEFT DOUBLE QUOTATION MARK}\N{LEFT SINGLE QUOTATION MARK}]) ')


def detokenize(text: str) -> str:
    """Remove the spaces a treebank puts around punctuation, to approximate the written text."""
    return _SPACE_AFTER.sub('', _SPACE_BEFORE.sub('', text))


def _gold_spans(text: str, tokens: list[str]) -> list[tuple[int, int]] | None:
    spans, pos = [], 0
    for token in tokens:
        start = text.find(token, pos)
        if start < 0 or text[pos:start].strip():
            return None  # the tokens don't cover the text; the sentence is skipped
        spans.append((start, start + len(token)))
        pos = start + len(token)
    return spans if not text[pos:].strip() else None


def _score(gold: int, predicted: int, correct: int) -> tuple[float, float, float]:
    precision = correct / predicted if predicted else 0.0
    recall = correct / gold if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def evaluate(task: str, dataset: str | Path, backend: str | None = None, *, text: str = 'detokenized',
             **config: Any) -> Report:
    """Score ``backend`` (the task's default if None) for ``task`` on ``dataset``.

    ``dataset`` is a registered name (see :func:`datasets`) or a path to a CoNLL-U file.
    ``text='detokenized'`` (default) removes treebank spaces around punctuation first;
    ``text='given'`` uses each sentence's text as written in the file.

    - ``tokenize``: precision, recall and F1 of token character spans.
    - ``sentences``: the sentences are joined into one text; precision, recall and F1 of the
      sentence end positions.

    Both run the full pipeline (normalize, then tokenize) and map results back to the original
    text through the alignment, so normalization doesn't affect the comparison.
    """
    if task not in TASKS:
        raise ValueError(f'cannot evaluate {task!r}; supported tasks: {", ".join(TASKS)}')
    if text not in ('detokenized', 'given'):
        raise ValueError(f"text={text!r}; choose 'detokenized' or 'given'")
    if str(dataset) in _datasets:
        name, path = str(dataset), resource_path(_datasets[str(dataset)].resource)
    else:
        name, path = Path(dataset).name, Path(dataset)
    sentences = read_conllu(path)
    prepare = detokenize if text == 'detokenized' else (lambda t: t)
    normalizer = get_backend('normalize')
    tokenizer = get_backend('tokenize', backend if task == 'tokenize' else None, **(config if task == 'tokenize' else {}))
    gold_n = predicted_n = correct = skipped = 0

    if task == 'tokenize':
        for sentence in sentences:
            raw = prepare(sentence.text)
            gold = _gold_spans(raw, sentence.tokens)
            if gold is None:
                skipped += 1
                continue
            doc = tokenizer(normalizer(Doc(raw)))
            predicted = {doc.to_raw(t) for t in doc.tokens}
            gold_n, predicted_n, correct = gold_n + len(gold), predicted_n + len(predicted), correct + len(predicted & set(gold))
    else:
        splitter = get_backend('sentences', backend, **config)
        raw = ' '.join(prepare(s.text) for s in sentences)
        gold, pos = set(), 0
        for sentence in sentences:
            pos += len(prepare(sentence.text))
            gold.add(pos)
            pos += 1
        doc = splitter(tokenizer(normalizer(Doc(raw))))
        predicted = {doc.to_raw(span)[1] for span in doc.sents}
        gold_n, predicted_n, correct = len(gold), len(predicted), len(predicted & gold)

    scored = tokenizer if task == 'tokenize' else splitter
    precision, recall, f1 = _score(gold_n, predicted_n, correct)
    counts = {'sentences': len(sentences), 'skipped': skipped, 'gold': gold_n, 'predicted': predicted_n,
              'correct': correct}
    return Report(task, scored.name, name, precision, recall, f1, counts)


def accuracy_table() -> str:
    """Evaluate the default backends on every registered dataset, as a Markdown table."""
    rows = ['| Task | Backend | Dataset | Precision | Recall | F1 |', '| --- | --- | --- | --- | --- | --- |']
    for dataset in datasets():
        for task in dataset.tasks:
            r = evaluate(task, dataset.name)
            rows.append(f'| {r.task} | {r.backend} | {r.dataset} | {r.precision:.3f} | {r.recall:.3f} | {r.f1:.3f} |')
    return '\n'.join(rows)
