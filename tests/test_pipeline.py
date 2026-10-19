import unittest

from sinling import Doc, PipelineError, UnknownBackendError, pipeline

from helpers import RegistryTestCase


class PipelineTest(RegistryTestCase):
    def test_runs_steps_in_order(self):
        doc = pipeline(['upper', 'split'])('ab cd')
        self.assertEqual(doc.raw, 'ab cd')
        self.assertEqual(doc.text, 'AB CD')
        self.assertEqual([t.text for t in doc.tokens], ['AB', 'CD'])
        self.assertEqual(doc.to_raw(doc.tokens[1]), (3, 5))

    def test_accepts_a_doc(self):
        doc = Doc('ab')
        self.assertIs(pipeline(['upper'])(doc), doc)

    def test_step_forms(self):
        nlp = pipeline([('upper', 'simple'), ('split', 'space', {}), {'task': 'split', 'backend': 'space'}])
        self.assertEqual(len(nlp.steps), 3)
        self.assertEqual(repr(nlp), 'Pipeline([upper:simple, split:space, split:space])')

    def test_text_changes_must_come_first(self):
        with self.assertRaisesRegex(PipelineError, "must come before 'split'"):
            pipeline(['split', 'upper'])

    def test_invalid_step(self):
        with self.assertRaises(PipelineError):
            pipeline([('upper',)])
        with self.assertRaises(PipelineError):
            pipeline([{'task': 'upper', 'model': 'x'}])

    def test_backends_are_built_when_the_pipeline_is(self):
        with self.assertRaises(UnknownBackendError):
            pipeline([('split', 'crf')])


if __name__ == '__main__':
    unittest.main()
