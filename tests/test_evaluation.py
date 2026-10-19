import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import sinling
from sinling.__main__ import main
from sinling.evaluation import datasets, detokenize, evaluate, read_conllu

FIXTURE = Path(__file__).parent / 'data' / 'eval_fixture.conllu'


class ConlluTest(unittest.TestCase):
    def test_read_with_a_multiword_token(self):
        sentences = read_conllu(FIXTURE)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[2].tokens, ['පොතක්වත්', 'නැහැ', '(', 'දැන්', ')', '.'])
        self.assertEqual(sentences[2].lemmas[:2], ['පොත', 'වත්'])
        self.assertEqual(sentences[1].upos, ['PRON', 'VERB', 'PUNCT'])

    def test_text_comment_is_required(self):
        with tempfile.NamedTemporaryFile('w', suffix='.conllu', delete=False, encoding='utf-8') as f:
            f.write('1\tමම\tමම\tPRON\t_\t_\t0\troot\t_\t_\n')
        self.addCleanup(os.unlink, f.name)
        with self.assertRaisesRegex(ValueError, '# text'):
            read_conllu(f.name)

    def test_detokenize(self):
        self.assertEqual(detokenize('පොතක්වත් නැහැ ( දැන් ) .'), 'පොතක්වත් නැහැ (දැන්).')
        self.assertEqual(detokenize('එනවද ?'), 'එනවද?')


class EvaluateTest(unittest.TestCase):
    def test_tokenize(self):
        for text in ('detokenized', 'given'):
            report = evaluate('tokenize', FIXTURE, text=text)
            self.assertEqual((report.precision, report.recall, report.f1), (1.0, 1.0, 1.0), text)
            self.assertEqual(report.counts['gold'], 13)

    def test_sentences(self):
        report = evaluate('sentences', FIXTURE)
        self.assertEqual(report.f1, 1.0)
        self.assertEqual(report.counts, {'sentences': 3, 'skipped': 0, 'gold': 3, 'predicted': 3, 'correct': 3})

    def test_errors_lower_the_score(self):
        # treating "යනවා." as an abbreviation merges two gold tokens into one
        report = evaluate('tokenize', FIXTURE, extra_abbreviations=['යනවා.'])
        self.assertEqual((report.counts['gold'], report.counts['predicted'], report.counts['correct']), (13, 12, 11))
        self.assertAlmostEqual(report.precision, 11 / 12)
        self.assertAlmostEqual(report.recall, 11 / 13)

    def test_report(self):
        report = evaluate('tokenize', FIXTURE)
        self.assertIn('tokenize [rules] on eval_fixture.conllu: precision 1.000', str(report))
        self.assertEqual(report.to_dict()['counts']['sentences'], 3)

    def test_invalid_arguments(self):
        with self.assertRaisesRegex(ValueError, 'supported tasks'):
            evaluate('stem', FIXTURE)
        with self.assertRaisesRegex(ValueError, 'detokenized'):
            evaluate('tokenize', FIXTURE, text='raw')

    def test_registered_datasets(self):
        names = [d.name for d in datasets()]
        self.assertEqual(names, ['ud-sinhala-appuwa', 'ud-sinhala-stb'])
        self.assertTrue(all(d.license == 'CC BY-SA 4.0' for d in datasets()))
        self.assertIs(sinling.evaluate, evaluate)

    def test_command_line(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(['evaluate', '--task', 'sentences', '--dataset', str(FIXTURE)]), 0)
        self.assertIn('F1 1.000', out.getvalue())


@unittest.skipUnless(os.environ.get('SINLING_NETWORK_TESTS') == '1', 'set SINLING_NETWORK_TESTS=1 to download')
class TreebankTest(unittest.TestCase):
    """Downloads the UD Sinhala treebanks; guards against accuracy regressions."""

    def test_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ['SINLING_HOME'] = tmp
            try:
                floors = {('tokenize', 'ud-sinhala-stb'): 0.99, ('tokenize', 'ud-sinhala-appuwa'): 0.99,
                          ('sentences', 'ud-sinhala-stb'): 0.99, ('sentences', 'ud-sinhala-appuwa'): 0.95}
                for (task, dataset), floor in floors.items():
                    with self.subTest(task=task, dataset=dataset):
                        self.assertGreaterEqual(evaluate(task, dataset).f1, floor)
            finally:
                del os.environ['SINLING_HOME']


if __name__ == '__main__':
    unittest.main()
