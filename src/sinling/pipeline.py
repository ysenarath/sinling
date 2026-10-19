"""Pipelines: several tasks run in order on one Doc."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sinling.doc import Doc
from sinling.errors import PipelineError
from sinling.registry import Backend, Task, _call, get_backend, get_task

__all__ = ['Pipeline', 'pipeline']

StepSpec = str | tuple[str, str] | tuple[str, str, dict[str, Any]] | dict[str, Any]


class Pipeline:
    """Runs a fixed list of steps on a Doc. Backends are built once, when the pipeline is.

    Each step is a task name (default backend), a ``(task, backend)`` or
    ``(task, backend, config)`` tuple, or a dict with ``task`` and optional ``backend``
    and ``config`` keys. Steps that change the text must come before all other steps.
    """

    def __init__(self, steps: Iterable[StepSpec]) -> None:
        self.steps: list[tuple[Task, Backend]] = []
        first_fixed: str | None = None  # first step that needs the text to stay unchanged
        for i, spec in enumerate(steps):
            task_name, backend_name, config = _parse_step(i, spec)
            task = get_task(task_name)
            if task.changes_text and first_fixed is not None:
                raise PipelineError(
                    f'step {i} ({task.name!r}) changes the text, so it must come before {first_fixed!r}')
            if not task.changes_text and first_fixed is None:
                first_fixed = task.name
            self.steps.append((task, get_backend(task.name, backend_name, **config)))

    def __call__(self, data: str | Doc) -> Doc:
        doc = data if isinstance(data, Doc) else Doc(data)
        for _, backend in self.steps:
            doc = _call(backend, doc)
        return doc

    def __repr__(self) -> str:
        steps = ', '.join(f'{task.name}:{backend.name}' for task, backend in self.steps)
        return f'Pipeline([{steps}])'


def pipeline(steps: Iterable[StepSpec]) -> Pipeline:
    """Build a :class:`Pipeline`, e.g. ``sinling.pipeline(['normalize', 'tokenize'])``."""
    return Pipeline(steps)


def _parse_step(i: int, spec: StepSpec) -> tuple[str, str | None, dict[str, Any]]:
    if isinstance(spec, str):
        return spec, None, {}
    if isinstance(spec, tuple) and len(spec) in (2, 3):
        config = spec[2] if len(spec) == 3 else {}
        return spec[0], spec[1], dict(config)
    if isinstance(spec, dict) and 'task' in spec and set(spec) <= {'task', 'backend', 'config'}:
        return spec['task'], spec.get('backend'), dict(spec.get('config', {}))
    raise PipelineError(
        f'step {i} must be a task name, a (task, backend[, config]) tuple '
        f'or a dict with task, backend and config keys; got {spec!r}')
