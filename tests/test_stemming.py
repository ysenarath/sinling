import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sinling
from sinling import Doc, DocError, ResourceUnavailableError, pipeline
from sinling.stemming import STEM_DICTIONARY, SUFFIXES, DictionaryStemmer, SuffixStemmer

ZWJ = '\N{ZERO WIDTH JOINER}'

# Small stand-ins for the upstream files, with the same quirks: a byte order mark glued to the
# first entry ('ක'), duplicates and a blank line.
SUFFIX_FIXTURE = '\N{ZERO WIDTH NO-BREAK SPACE}ක\nට\nක්\nයක්\nීමට\n්වලින්\nවලින්\nට\n\n'
DICTIONARY_FIXTURE = 'අංකයක්\tඅංක\nඉන්දීය\tඉන්දියාව\nපිහිටවීමට\tපිහිටවීම\nප්රශ්නයට\tප්රශ්නය\nbroken line\n'


class FixtureTestCase(unittest.TestCase):
    """Puts fixture copies of both resources in a temporary cache, so no download happens."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        env = mock.patch.dict(os.environ, {'SINLING_HOME': tmp.name, 'SINLING_OFFLINE': '1'})
        env.start()
        self.addCleanup(env.stop)
        for resource, content in ((SUFFIXES, SUFFIX_FIXTURE), (STEM_DICTIONARY, DICTIONARY_FIXTURE)):
            resource.path.parent.mkdir(parents=True)
            resource.path.write_text(content, encoding='utf-8')


class SuffixStemmerTest(FixtureTestCase):
    def test_strips_the_longest_suffix(self):
        stemmer = SuffixStemmer()
        self.assertEqual(stemmer.split('පිහිටවීමට'), ('පිහිටව', 'ීමට'))
        self.assertEqual(stemmer.split('පොත්වලින්'), ('පොත', '්වලින්'))
        self.assertEqual(stemmer.split('ඇත'), ('ඇත', ''))

    def test_a_word_that_is_a_suffix_is_not_emptied(self):
        stemmer = SuffixStemmer()
        self.assertEqual(stemmer.split('ට'), ('ට', ''))
        self.assertEqual(stemmer.split('යක්'), ('යක්', ''))

    def test_bare_ka_is_not_a_suffix(self):
        self.assertEqual(SuffixStemmer().split('නායක'), ('නායක', ''))

    def test_annotates_word_tokens_only(self):
        doc = pipeline(['tokenize'])('පොත්වලින් 500ක් ගත්තා.')
        SuffixStemmer()(doc)
        self.assertEqual([(t.attrs['stem'], t.attrs['suffix']) for t in doc.tokens],
                         [('පොත', '්වලින්'), ('500', 'ක්'), ('ගත්තා', ''), ('.', '')])

    def test_needs_tokens(self):
        with self.assertRaisesRegex(DocError, 'tokenize'):
            SuffixStemmer()(Doc('පොත්වලින්'))


class DictionaryStemmerTest(FixtureTestCase):
    def test_dictionary_then_suffixes(self):
        stemmer = DictionaryStemmer()
        self.assertEqual(stemmer.split('අංකයක්'), ('අංක', 'යක්'))
        self.assertEqual(stemmer.split('පිහිටවීමට'), ('පිහිටවීම', 'ට'))
        self.assertEqual(stemmer.split('පොත්වලින්'), ('පොත', '්වලින්'))

    def test_spelling_normalization_has_empty_suffix(self):
        self.assertEqual(DictionaryStemmer().split('ඉන්දීය'), ('ඉන්දියාව', ''))

    def test_joiners_in_the_word_are_kept(self):
        # the dictionary has no ZWJ conjuncts; normalized text does
        self.assertEqual(DictionaryStemmer().split(f'ප්{ZWJ}රශ්නයට'), (f'ප්{ZWJ}රශ්නය', 'ට'))


class ResourceTest(unittest.TestCase):
    def test_offline_without_cache_explains_how_to_download(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.dict(os.environ, {'SINLING_HOME': tmp, 'SINLING_OFFLINE': '1'}):
            with self.assertRaisesRegex(ResourceUnavailableError, "sinling.download\\('sinhala-suffixes'\\)"):
                SuffixStemmer()

    def test_resources_point_at_a_pinned_upstream_commit(self):
        for resource in (SUFFIXES, STEM_DICTIONARY):
            self.assertIn('/rksk/sinhala-news-analysis/05e7076caa76bfe490f93d221c4aac88c1d01600/', resource.url)
            self.assertEqual(len(resource.sha256), 64)

    def test_listed_as_online_backends(self):
        info = {b.name: (b.default, b.offline) for b in sinling.backends('stem')}
        self.assertEqual(info, {'dictionary': (False, False), 'suffix': (True, False)})


@unittest.skipUnless(os.environ.get('SINLING_NETWORK_TESTS') == '1', 'set SINLING_NETWORK_TESTS=1 to download')
class UpstreamDataTest(unittest.TestCase):
    """Downloads the real files and checks the results 0.3.7's tests expected."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.env = mock.patch.dict(os.environ, {'SINLING_HOME': cls.tmp.name})
        cls.env.start()
        os.environ.pop('SINLING_OFFLINE', None)

    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        cls.tmp.cleanup()

    def test_suffix_stemmer(self):
        stemmer = SuffixStemmer()
        self.assertEqual(stemmer.split('පිහිටවීමට'), ('පිහිටව', 'ීමට'))
        self.assertEqual(stemmer.split('පොත්වලින්'), ('පොත', '්වලින්'))
        self.assertEqual(stemmer.split('ඇත'), ('ඇත', ''))
        self.assertEqual(stemmer.split('ට'), ('ට', ''))
        self.assertEqual(stemmer.split('යක්'), ('යක්', ''))

    def test_dictionary_stemmer(self):
        stemmer = DictionaryStemmer()
        self.assertEqual(stemmer.split('අංකයක්'), ('අංක', 'යක්'))
        self.assertEqual(stemmer.split('පිහිටවීමට'), ('පිහිටවීම', 'ට'))
        self.assertEqual(stemmer.split('ඉන්දීය'), ('ඉන්දියාව', ''))

    def test_stem_function(self):
        self.assertEqual(sinling.stem('පොත්වලින් කියවන්න.'), ['පොත', 'කියව', '.'])
        self.assertTrue(Path(SUFFIXES.path).exists())


if __name__ == '__main__':
    unittest.main()
