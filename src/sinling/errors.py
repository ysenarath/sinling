"""Exceptions raised by Sinling."""


class SinlingError(Exception):
    """Base class for all errors raised by Sinling."""


class UnknownTaskError(SinlingError, LookupError):
    """No task is defined under the requested name."""


class UnknownBackendError(SinlingError, LookupError):
    """No backend is registered under the requested task and name."""


class MissingDependencyError(SinlingError, ImportError):
    """A backend needs an optional dependency that isn't installed."""


class DocError(SinlingError, ValueError):
    """An operation would leave a Doc in an inconsistent state."""


class PipelineError(SinlingError, ValueError):
    """A pipeline is misconfigured, e.g. its steps are in an invalid order."""


class UnknownResourceError(SinlingError, LookupError):
    """No resource is registered under the requested name."""


class ResourceUnavailableError(SinlingError, OSError):
    """A resource is not cached and can't be downloaded."""


class ResourceIntegrityError(SinlingError, OSError):
    """A downloaded resource doesn't match its expected size or checksum."""
