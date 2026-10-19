import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sinling import (
    ResourceIntegrityError,
    ResourceUnavailableError,
    UnknownResourceError,
    download,
    resources,
)
from sinling.resources import Resource, register_resource, resource_path

CONTENT = 'ගෙදර\tගෙදර\n'.encode()


class ResourceTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name) / 'cache'
        self.source = Path(tmp.name) / 'stems-1.0.tsv'
        self.source.write_bytes(CONTENT)
        env = mock.patch.dict(os.environ, {'SINLING_HOME': str(self.home)})
        env.start()
        self.addCleanup(env.stop)
        os.environ.pop('SINLING_OFFLINE', None)
        saved = dict(resources._resources)
        self.addCleanup(lambda: (resources._resources.clear(), resources._resources.update(saved)))

    def add(self, name='stems', sha256=None, size=None):
        return register_resource(Resource(
            name, '1.0', self.source.as_uri(), sha256 or hashlib.sha256(CONTENT).hexdigest(), size))

    def test_downloads_once_into_versioned_cache(self):
        res = self.add(size=len(CONTENT))
        path = resource_path('stems')
        self.assertEqual(path, self.home / 'stems' / '1.0' / 'stems-1.0.tsv')
        self.assertEqual(path.read_bytes(), CONTENT)
        self.source.unlink()
        self.assertEqual(resource_path('stems'), res.path)  # served from the cache

    def test_checksum_mismatch_leaves_nothing_behind(self):
        res = self.add(sha256='0' * 64)
        with self.assertRaises(ResourceIntegrityError):
            download('stems')
        self.assertFalse(res.path.exists())
        self.assertEqual(list(res.path.parent.iterdir()), [])

    def test_size_mismatch(self):
        self.add(size=1)
        with self.assertRaises(ResourceIntegrityError):
            download('stems')

    def test_offline_mode_refuses_to_download(self):
        self.add()
        with mock.patch.dict(os.environ, {'SINLING_OFFLINE': '1'}):
            with self.assertRaisesRegex(ResourceUnavailableError, r"sinling.download\('stems'\)"):
                resource_path('stems')

    def test_offline_mode_uses_the_cache(self):
        self.add()
        download('stems')
        with mock.patch.dict(os.environ, {'SINLING_OFFLINE': 'true'}):
            self.assertEqual(resource_path('stems').read_bytes(), CONTENT)

    def test_force_downloads_again(self):
        res = self.add()
        download('stems')
        res.path.write_bytes(b'stale')
        download('stems', force=True)
        self.assertEqual(res.path.read_bytes(), CONTENT)

    def test_unreachable_source(self):
        self.add()
        self.source.unlink()
        with self.assertRaises(ResourceUnavailableError):
            download('stems')

    def test_unknown_resource(self):
        with self.assertRaises(UnknownResourceError):
            resource_path('nope')

    def test_only_https_urls(self):
        with self.assertRaisesRegex(ValueError, 'https'):
            register_resource(Resource('x', '1', 'http://example.com/x.tsv', '0' * 64))

    def test_conflicting_registration(self):
        self.add()
        with self.assertRaises(ValueError):
            self.add(sha256='1' * 64)

    def test_default_cache_dir(self):
        with mock.patch.dict(os.environ, {'SINLING_HOME': '', 'XDG_CACHE_HOME': '/tmp/xdg'}):
            self.assertEqual(resources.cache_dir(), Path('/tmp/xdg/sinling'))


if __name__ == '__main__':
    unittest.main()
