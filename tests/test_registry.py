import unittest
from importlib.metadata import EntryPoint
from unittest import mock

import sinling
from sinling import (
    Backend,
    Doc,
    MissingDependencyError,
    UnknownBackendError,
    UnknownTaskError,
    backends,
    register,
    registry,
)
from sinling.registry import define_task, get_backend, run_task

from helpers import RegistryTestCase


def _entry_points(*specs):
    return [EntryPoint(name, value, registry.ENTRY_POINT_GROUP) for name, value in specs]


class TaskTest(RegistryTestCase):
    def test_run_task_returns_plain_value(self):
        self.assertEqual(run_task('upper', 'abc'), 'ABC')
        self.assertEqual(run_task('split', 'a b  c'), ['a', 'b', 'c'])

    def test_run_task_accepts_a_doc(self):
        doc = Doc('ab')
        self.assertEqual(run_task('upper', doc), 'AB')
        self.assertEqual(doc.text, 'AB')

    def test_unknown_task(self):
        with self.assertRaisesRegex(UnknownTaskError, 'split, upper'):
            run_task('parse', 'x')

    def test_task_names_are_unique_and_dotless(self):
        with self.assertRaises(ValueError):
            define_task('upper', lambda doc: doc.text)
        with self.assertRaises(ValueError):
            define_task('a.b', lambda doc: doc.text)

    def test_backend_must_return_a_doc(self):
        @register('split', 'broken')
        class Broken(Backend):
            def __call__(self, doc):
                return None

        with self.assertRaisesRegex(TypeError, 'returned NoneType'):
            run_task('split', 'a', backend='broken')


class RegisterTest(RegistryTestCase):
    def test_register_sets_task_and_name(self):
        @register('split', 'chars')
        class Chars(Backend):
            pass

        self.assertEqual((Chars.task, Chars.name), ('split', 'chars'))

    def test_register_needs_a_known_task(self):
        with self.assertRaises(UnknownTaskError):
            register('parse', 'x')

    def test_duplicate_backend_or_default_is_rejected(self):
        with self.assertRaises(ValueError):
            register('split', 'space')(type('Again', (Backend,), {}))
        with self.assertRaises(ValueError):
            register('split', 'other', default=True)(type('Other', (Backend,), {}))

    def test_only_backend_subclasses(self):
        with self.assertRaises(TypeError):
            register('split', 'bad')(object)


class GetBackendTest(RegistryTestCase):
    def test_default_backend(self):
        self.assertEqual(get_backend('split').name, 'space')

    def test_task_without_default(self):
        define_task('tag', lambda doc: doc.tokens)
        with self.assertRaisesRegex(UnknownBackendError, 'no default'):
            get_backend('tag')

    def test_unknown_backend_lists_available(self):
        with self.assertRaisesRegex(UnknownBackendError, 'available: space'):
            get_backend('split', 'crf')

    def test_instances_are_cached_by_config(self):
        a = get_backend('split', 'space', size=1)
        self.assertIs(get_backend('split', 'space', size=1), a)
        self.assertIsNot(get_backend('split', 'space', size=2), a)
        self.assertEqual(a.config, {'size': 1})

    def test_config_may_use_any_key(self):
        self.assertEqual(get_backend('split', 'space', name='x', task='y').config, {'name': 'x', 'task': 'y'})
        self.assertEqual(run_task('split', 'a b', data='z'), ['a', 'b'])

    def test_unhashable_config_is_not_cached(self):
        a = get_backend('split', 'space', labels=['x'])
        self.assertIsNot(get_backend('split', 'space', labels=['x']), a)

    def test_missing_dependency_names_the_extra(self):
        @register('split', 'heavy')
        class Heavy(Backend):
            extra = 'crf'
            requires = ('sinling_module_that_does_not_exist',)

        with self.assertRaisesRegex(MissingDependencyError, r'pip install "sinling\[crf\]"'):
            get_backend('split', 'heavy')

    def test_missing_dependency_without_extra(self):
        @register('split', 'heavy')
        class Heavy(Backend):
            requires = ('sinling_module_that_does_not_exist',)

        with self.assertRaisesRegex(MissingDependencyError, 'pip install sinling_module_that_does_not_exist'):
            get_backend('split', 'heavy')


class PluginTest(RegistryTestCase):
    def use_plugins(self, *specs):
        registry._registry._plugins = None
        patcher = mock.patch.object(registry, 'entry_points', return_value=_entry_points(*specs))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_plugin_is_listed_before_it_is_loaded(self):
        self.use_plugins(('upper.shout', 'fake_plugin:ShoutBackend'))
        info = [b for b in backends('upper') if b.name == 'shout'][0]
        self.assertEqual(info.source, 'plugin')
        self.assertIsNone(info.available)

    def test_plugin_loads_on_first_use(self):
        self.use_plugins(('upper.shout', 'fake_plugin:ShoutBackend'))
        self.assertEqual(run_task('upper', 'ab', backend='shout'), 'ab!')
        info = [b for b in backends('upper') if b.name == 'shout'][0]
        self.assertTrue(info.available)
        self.assertEqual(info.downloads, ())

    def test_plugin_must_be_a_backend(self):
        self.use_plugins(('upper.bad', 'fake_plugin:NotABackend'))
        with self.assertRaisesRegex(TypeError, 'not a Backend subclass'):
            get_backend('upper', 'bad')

    def test_malformed_entry_point_is_skipped_with_warning(self):
        self.use_plugins(('nodot', 'fake_plugin:ShoutBackend'))
        with self.assertWarnsRegex(UserWarning, 'nodot'):
            self.assertEqual([b.name for b in backends('upper')], ['simple'])


class BackendsTest(RegistryTestCase):
    def test_lists_builtins_with_details(self):
        info = backends('split')
        self.assertEqual(len(info), 1)
        self.assertEqual(info[0].name, 'space')
        self.assertTrue(info[0].default)
        self.assertEqual(info[0].source, 'builtin')
        self.assertTrue(info[0].available)

    def test_lists_all_tasks(self):
        self.assertEqual([(b.task, b.name) for b in backends()], [('split', 'space'), ('upper', 'simple')])

    def test_unknown_task(self):
        with self.assertRaises(UnknownTaskError):
            backends('parse')


class PublicApiTest(unittest.TestCase):
    def test_exports_resolve(self):
        for name in sinling.__all__:
            self.assertTrue(hasattr(sinling, name), name)

    def test_version_comes_from_metadata(self):
        self.assertTrue(sinling.__version__.startswith('0.4'))


if __name__ == '__main__':
    unittest.main()
