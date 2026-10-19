"""Sinling: a language processing toolkit for Sinhala.

The top level holds the user API: task functions, the document classes, pipelines and errors.
Plugin authors find ``define_task``, ``get_backend`` and ``run_task`` in ``sinling.registry``, and
``Resource`` and ``register_resource`` in ``sinling.resources``.
"""

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
from sinling.registry import Backend, backends, register
from sinling.resources import download
from sinling.normalization import normalize
from sinling.script import aksharas
from sinling.tokenization import sentences, tokenize
from sinling.stemming import stem
from sinling.legacy_fonts import from_legacy_font
from sinling.evaluation import evaluate

try:
    __version__ = version('sinling')
except PackageNotFoundError:  # imported from a source checkout without installing
    __version__ = '0+unknown'

__all__ = [
    # tasks
    'aksharas', 'from_legacy_font', 'normalize', 'sentences', 'stem', 'tokenize',
    # documents and pipelines
    'Doc', 'Pipeline', 'Span', 'Token', 'pipeline',
    # backends, resources and evaluation
    'Backend', 'backends', 'download', 'evaluate', 'register',
    # errors
    'DocError', 'MissingDependencyError', 'PipelineError', 'ResourceIntegrityError',
    'ResourceUnavailableError', 'SinlingError', 'UnknownBackendError', 'UnknownResourceError',
    'UnknownTaskError',
]
