import unittest

from sinling import SinhalaStemmer


class SinhalaStemmerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stemmer = SinhalaStemmer()
        cls.suffix_only = SinhalaStemmer(use_dictionary=False)

    def test_dictionary_is_loaded_by_word(self):
        self.assertIn('අංකයක්', self.stemmer.stem_dictionary)
        self.assertEqual(self.stemmer.stem('අංකයක්'), ('අංක', 'යක්'))
        self.assertEqual(self.stemmer.stem('පිහිටවීමට'), ('පිහිටවීම', 'ට'))

    def test_dictionary_normalization_has_empty_suffix(self):
        # the dictionary stem is not a prefix of the word
        self.assertEqual(self.stemmer.stem('ඉන්දීය'), ('ඉන්දියාව', ''))

    def test_suffix_stripping_without_dictionary_entry(self):
        self.assertEqual(self.stemmer.stem('පොත්වලින්'), ('පොත', '්වලින්'))

    def test_dictionary_can_be_disabled(self):
        self.assertEqual(self.suffix_only.stem_dictionary, {})
        self.assertEqual(self.suffix_only.stem('පිහිටවීමට'), ('පිහිටව', 'ීමට'))

    def test_word_without_known_suffix_is_unchanged(self):
        self.assertEqual(self.stemmer.stem('ඇත'), ('ඇත', ''))

    def test_word_that_is_a_suffix_is_not_emptied(self):
        self.assertEqual(self.stemmer.stem('ට'), ('ට', ''))
        self.assertEqual(self.stemmer.stem('යක්'), ('යක්', ''))


if __name__ == '__main__':
    unittest.main()
