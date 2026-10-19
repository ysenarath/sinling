import inspect
import unittest

import sinling
from sinling import pipeline


class DefaultPipelineTest(unittest.TestCase):
    def test_no_steps_means_normalize_tokenize_sentences(self):
        nlp = pipeline()
        self.assertEqual([task.name for task, _ in nlp.steps], ['normalize', 'tokenize', 'sentences'])
        doc = nlp('\N{SINHALA VOWEL SIGN KOMBUVA}ගදර යනවා. ඔයා එනවද?')
        self.assertEqual([t.text for t in doc.tokens], ['ගෙදර', 'යනවා', '.', 'ඔයා', 'එනවද', '?'])
        self.assertEqual(len(doc.sents), 2)


class SignatureTest(unittest.TestCase):
    """Every task function takes the text, then keyword-only backend= and options."""

    def test_task_functions_share_one_shape(self):
        for name in ('normalize', 'tokenize', 'sentences', 'stem', 'from_legacy_font'):
            with self.subTest(name=name):
                params = list(inspect.signature(getattr(sinling, name)).parameters.values())
                self.assertEqual(params[0].name, 'text')
                self.assertEqual(params[0].kind, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                self.assertTrue(all(p.kind in (p.KEYWORD_ONLY, p.VAR_KEYWORD) for p in params[1:]))
                self.assertIn('backend', [p.name for p in params])
                self.assertEqual(params[-1].kind, inspect.Parameter.VAR_KEYWORD)

    def test_top_level_is_the_user_api(self):
        for internal in ('define_task', 'run_task', 'get_backend', 'register_resource', 'resource_path'):
            self.assertNotIn(internal, sinling.__all__)
        self.assertEqual(len(sinling.__all__), len(set(sinling.__all__)))


if __name__ == '__main__':
    unittest.main()
