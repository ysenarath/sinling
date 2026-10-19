"""Tasks, backends and the registry that connects them.

A *task* is something Sinling can do (``normalize``, ``tokenize``, ``ner``). A *backend* is
one way of doing it, implemented as a :class:`Backend` subclass. Built-in backends register
with the :func:`register` decorator; plugins register through the ``sinling.backends``
entry-point group, named ``<task>.<backend>``::

    [project.entry-points."sinling.backends"]
    "ner.transformer" = "sinling_ner_hf:TransformerNER"

Plugins are imported only when one of their backends is first used.
"""

from __future__ import annotations

import importlib.util
import warnings
from collections.abc import Callable
from dataclasses import dataclass
from importlib.metadata import EntryPoint, entry_points
from typing import Any, ClassVar

from sinling.doc import Doc
from sinling.errors import MissingDependencyError, UnknownBackendError, UnknownTaskError

__all__ = [
    'ENTRY_POINT_GROUP', 'Backend', 'BackendInfo', 'Task',
    'backends', 'define_task', 'get_backend', 'get_task', 'register', 'run_task',
]

ENTRY_POINT_GROUP = 'sinling.backends'


@dataclass(frozen=True)
class Task:
    """A task: its name, what it returns as a plain value, and whether it changes the text."""

    name: str
    output: Callable[[Doc], Any]
    changes_text: bool = False
    description: str = ''


class Backend:
    """Base class for backends. Subclasses annotate a :class:`Doc` in ``__call__``.

    Class attributes describe the backend: the optional-dependency ``extra`` that installs
    what it ``requires`` (importable module names), and the ``resources`` it downloads on
    first use (none means it works without any download).
    """

    task: ClassVar[str] = ''
    name: ClassVar[str] = ''
    extra: ClassVar[str | None] = None
    requires: ClassVar[tuple[str, ...]] = ()
    resources: ClassVar[tuple[str, ...]] = ()

    def __init__(self, **config: Any) -> None:
        self.config = config

    def __call__(self, doc: Doc) -> Doc:
        raise NotImplementedError


@dataclass(frozen=True)
class BackendInfo:
    """What :func:`backends` reports about a backend.

    ``downloads`` names the resources fetched on first use; an empty tuple means the backend
    works without any download. For a plugin that hasn't been loaded yet, ``extra``,
    ``downloads`` and ``available`` are None.
    """

    task: str
    name: str
    default: bool
    source: str
    extra: str | None
    downloads: tuple[str, ...] | None
    available: bool | None


class _Registry:
    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}
        self.backends: dict[tuple[str, str], type[Backend]] = {}
        self.sources: dict[tuple[str, str], str] = {}
        self.defaults: dict[str, str] = {}
        self.instances: dict[tuple[Any, ...], Backend] = {}
        self._plugins: dict[tuple[str, str], EntryPoint] | None = None

    @property
    def plugins(self) -> dict[tuple[str, str], EntryPoint]:
        if self._plugins is None:
            self._plugins = {}
            for ep in entry_points(group=ENTRY_POINT_GROUP):
                task, _, name = ep.name.partition('.')
                if not task or not name:
                    warnings.warn(f'ignoring entry point {ep.name!r}: expected "<task>.<backend>"', stacklevel=2)
                    continue
                self._plugins.setdefault((task, name), ep)
        return self._plugins

    def load_plugin(self, key: tuple[str, str]) -> type[Backend]:
        ep = self.plugins[key]
        cls = ep.load()
        if not (isinstance(cls, type) and issubclass(cls, Backend)):
            raise TypeError(f'entry point {ep.name!r} ({ep.value}) is not a Backend subclass')
        if key not in self.backends:
            cls.task, cls.name = key
            self.backends[key] = cls
            self.sources[key] = ep.dist.name if ep.dist is not None else 'plugin'
        return self.backends[key]


_registry = _Registry()


def define_task(name: str, output: Callable[[Doc], Any], *, changes_text: bool = False,
                description: str = '') -> Task:
    """Define a new task. ``output`` turns an annotated Doc into the task's plain return value."""
    if not name or '.' in name:
        raise ValueError(f'invalid task name {name!r}: it must be non-empty and contain no dots')
    if name in _registry.tasks:
        raise ValueError(f'task {name!r} is already defined')
    task = Task(name, output, changes_text, description)
    _registry.tasks[name] = task
    return task


def get_task(name: str) -> Task:
    try:
        return _registry.tasks[name]
    except KeyError:
        known = ', '.join(sorted(_registry.tasks)) or 'none'
        raise UnknownTaskError(f'unknown task {name!r}; defined tasks: {known}') from None


def register(task: str, name: str, *, default: bool = False) -> Callable[[type[Backend]], type[Backend]]:
    """Class decorator that registers a built-in backend for ``task`` under ``name``."""
    get_task(task)

    def decorator(cls: type[Backend]) -> type[Backend]:
        if not (isinstance(cls, type) and issubclass(cls, Backend)):
            raise TypeError(f'{cls!r} is not a Backend subclass')
        key = (task, name)
        if key in _registry.backends:
            raise ValueError(f'backend {name!r} is already registered for task {task!r}')
        cls.task, cls.name = key
        _registry.backends[key] = cls
        _registry.sources[key] = 'builtin'
        if default:
            if task in _registry.defaults:
                raise ValueError(f'task {task!r} already has a default backend ({_registry.defaults[task]!r})')
            _registry.defaults[task] = name
        return cls

    return decorator


def _backend_class(task: str, name: str) -> type[Backend]:
    key = (task, name)
    if key in _registry.backends:
        return _registry.backends[key]
    if key in _registry.plugins:
        return _registry.load_plugin(key)
    names = sorted({n for t, n in [*_registry.backends, *_registry.plugins] if t == task})
    raise UnknownBackendError(
        f'unknown backend {name!r} for task {task!r}; available: {", ".join(names) or "none"}')


def _check_requirements(cls: type[Backend]) -> None:
    missing = [module for module in cls.requires if importlib.util.find_spec(module) is None]
    if missing:
        install = f'pip install "sinling[{cls.extra}]"' if cls.extra else f'pip install {" ".join(missing)}'
        raise MissingDependencyError(
            f'backend {cls.name!r} for task {cls.task!r} needs {", ".join(missing)}: {install}')


def _freeze(config: dict[str, Any]) -> tuple[Any, ...] | None:
    key = tuple(sorted(config.items()))
    try:
        hash(key)
    except TypeError:
        return None
    return key


def get_backend(task: str, name: str | None = None, /, **config: Any) -> Backend:
    """Return a ready backend instance, the task's default when ``name`` is None.

    Instances are cached by task, name and config, so models load once.
    """
    get_task(task)
    if name is None:
        if task not in _registry.defaults:
            raise UnknownBackendError(f'task {task!r} has no default backend; pass backend=')
        name = _registry.defaults[task]
    cls = _backend_class(task, name)
    _check_requirements(cls)
    frozen = _freeze(config)
    if frozen is None:
        return cls(**config)
    key = (task, name, frozen)
    if key not in _registry.instances:
        _registry.instances[key] = cls(**config)
    return _registry.instances[key]


def run_task(task: str, data: str | Doc, /, backend: str | None = None, **config: Any) -> Any:
    """Run one task on a string or Doc and return the task's plain value."""
    spec = get_task(task)
    doc = data if isinstance(data, Doc) else Doc(data)
    return spec.output(_call(get_backend(task, backend, **config), doc))


def _call(backend: Backend, doc: Doc) -> Doc:
    result = backend(doc)
    if not isinstance(result, Doc):
        raise TypeError(f'backend {backend.name!r} for task {backend.task!r} returned '
                        f'{type(result).__name__}, not a Doc')
    return result


def backends(task: str | None = None) -> list[BackendInfo]:
    """List registered and installed-plugin backends, optionally for one task."""
    if task is not None:
        get_task(task)
    infos = []
    for key in sorted({*_registry.backends, *_registry.plugins}):
        t, name = key
        if task is not None and t != task:
            continue
        default = _registry.defaults.get(t) == name
        cls = _registry.backends.get(key)
        if cls is None:
            ep = _registry.plugins[key]
            source = ep.dist.name if ep.dist is not None else 'plugin'
            infos.append(BackendInfo(t, name, default, source, None, None, None))
            continue
        available = all(importlib.util.find_spec(m) is not None for m in cls.requires)
        infos.append(BackendInfo(t, name, default, _registry.sources[key], cls.extra, tuple(cls.resources), available))
    return infos
