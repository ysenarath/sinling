"""Sinling: a language processing toolkit for Sinhala."""

from importlib.metadata import PackageNotFoundError, version

from sinling.doc import Doc, Span, Token
from sinling.errors import (
    DocError,
    MissingDependencyError,
    PipelineError,
    ResourceIntegrityError,
    ResourceUnavailableError,
    SinlingError,
    UnknownBackendError,
    UnknownResourceError,
    UnknownTaskError,
)
from sinling.pipeline import Pipeline, pipeline
from sinling.registry import Backend, BackendInfo, Task, backends, define_task, get_backend, register, run_task
from sinling.resources import Resource, download, register_resource, resource_path
from sinling.normalization import normalize
from sinling.script import aksharas
from sinling.tokenization import sentences, tokenize
from sinling.stemming import stem

try:
    __version__ = version('sinling')
except PackageNotFoundError:  # imported from a source checkout without installing
    __version__ = '0+unknown'

__all__ = [
    'Backend', 'BackendInfo', 'Doc', 'Pipeline', 'Resource', 'Span', 'Task', 'Token',
    'aksharas', 'backends', 'define_task', 'download', 'get_backend', 'normalize', 'pipeline', 'register',
    'sentences', 'stem', 'tokenize',
    'register_resource', 'resource_path', 'run_task',
    'DocError', 'MissingDependencyError', 'PipelineError', 'ResourceIntegrityError',
    'ResourceUnavailableError', 'SinlingError', 'UnknownBackendError', 'UnknownResourceError',
    'UnknownTaskError',
]
