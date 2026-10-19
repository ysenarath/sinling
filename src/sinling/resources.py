"""Versioned data files (dictionaries, statistics, models) downloaded on first use.

Files are cached under ``~/.cache/sinling/<name>/<version>/``. Set ``SINLING_HOME`` to use
another directory, and ``SINLING_OFFLINE=1`` to forbid downloads.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from sinling.errors import ResourceIntegrityError, ResourceUnavailableError, UnknownResourceError

__all__ = ['Resource', 'cache_dir', 'download', 'is_offline', 'list_resources', 'register_resource', 'resource_path']

_ALLOWED_SCHEMES = {'https', 'file'}
_CHUNK = 1 << 20


@dataclass(frozen=True)
class Resource:
    """A downloadable file, pinned by version and SHA-256 checksum."""

    name: str
    version: str
    url: str
    sha256: str
    size: int | None = None
    license: str | None = None
    description: str = ''

    @property
    def filename(self) -> str:
        return Path(urllib.parse.urlparse(self.url).path).name

    @property
    def path(self) -> Path:
        """Where the file is (or will be) cached."""
        return cache_dir() / self.name / self.version / self.filename


_resources: dict[str, Resource] = {}


def register_resource(resource: Resource) -> Resource:
    scheme = urllib.parse.urlparse(resource.url).scheme
    if scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f'resource {resource.name!r} URL must use https, not {scheme or "no scheme"}')
    if not resource.filename:
        raise ValueError(f'resource {resource.name!r} URL does not end in a file name')
    existing = _resources.get(resource.name)
    if existing is not None and existing != resource:
        raise ValueError(f'resource {resource.name!r} is already registered with different details')
    _resources[resource.name] = resource
    return resource


def list_resources() -> list[Resource]:
    return sorted(_resources.values(), key=lambda r: r.name)


def get_resource(name: str) -> Resource:
    try:
        return _resources[name]
    except KeyError:
        known = ', '.join(sorted(_resources)) or 'none'
        raise UnknownResourceError(f'unknown resource {name!r}; registered: {known}') from None


def cache_dir() -> Path:
    if os.environ.get('SINLING_HOME'):
        return Path(os.environ['SINLING_HOME'])
    base = os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache'
    return Path(base) / 'sinling'


def is_offline() -> bool:
    return os.environ.get('SINLING_OFFLINE', '').strip().lower() in {'1', 'true', 'yes', 'on'}


def resource_path(name: str) -> Path:
    """Return the local path of a resource, downloading it first if needed and allowed."""
    resource = get_resource(name)
    if resource.path.exists():
        return resource.path
    return download(name)


def download(name: str, *, force: bool = False) -> Path:
    """Download a resource into the cache, verify its checksum and return its path."""
    resource = get_resource(name)
    target = resource.path
    if target.exists() and not force:
        return target
    if is_offline():
        raise ResourceUnavailableError(
            f'resource {name!r} {resource.version} is not cached at {target} and SINLING_OFFLINE is set. '
            f'Run sinling.download({name!r}) on a connected machine and copy {cache_dir()} here.')
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=f'.{target.name}.', suffix='.part')
    tmp = Path(tmp_name)
    try:
        digest, size = hashlib.sha256(), 0
        with os.fdopen(fd, 'wb') as out, urllib.request.urlopen(resource.url, timeout=60) as response:
            while chunk := response.read(_CHUNK):
                digest.update(chunk)
                size += len(chunk)
                out.write(chunk)
        if resource.size is not None and size != resource.size:
            raise ResourceIntegrityError(f'resource {name!r}: expected {resource.size} bytes, got {size}')
        if digest.hexdigest() != resource.sha256.lower():
            raise ResourceIntegrityError(f'resource {name!r}: SHA-256 does not match; the download may be corrupt')
        os.replace(tmp, target)
    except urllib.error.URLError as e:
        raise ResourceUnavailableError(f'could not download resource {name!r} from {resource.url}: {e.reason}') from e
    finally:
        tmp.unlink(missing_ok=True)
    return target
