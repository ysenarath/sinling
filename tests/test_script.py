import unittest

from sinling import aksharas
from sinling.script import CONSONANTS, INDEPENDENT_VOWELS, VOWEL_SIGNS, VOWEL_TO_SIGN, is_sinhala

from test_normalize import CASES


class AksharaTest(unittest.TestCase):
    def test_examples(self):
        examples = {
            'ශ්\u200dරී ලංකාව': ['ශ්\u200dරී', ' ', 'ලං', 'කා', 'ව'],
            'ඉංග්\u200dරීසි': ['ඉං', 'ග්\u200dරී', 'සි'],
            'ගෙදර': ['ගෙ', 'ද', 'ර'],
            'ස්ත': ['ස්', 'ත'],  # explicit al-lakuna: two aksharas
            'ක\u200d\u0dcaව': ['ක\u200d\u0dcaව'],  # touching letters: one
            'ර්\u200dක': ['ර්\u200dක'],  # repaya joins the next consonant
            'කෝ': ['කෝ'],
            'ab 1': ['a', 'b', ' ', '1'],
            'cafe\u0301': ['c', 'a', 'f', 'e\u0301'],
            '': [],
        }
        for text, expected in examples.items():
            with self.subTest(text=text):
                self.assertEqual(aksharas(text), expected)

    def test_lossless(self):
        for case in CASES:
            for text in (case['input'], case['expected']):
                with self.subTest(text=text):
                    self.assertEqual(''.join(aksharas(text)), text)


class TablesTest(unittest.TestCase):
    def test_classes_are_sinhala_and_disjoint(self):
        for chars in (CONSONANTS, INDEPENDENT_VOWELS, VOWEL_SIGNS):
            self.assertTrue(all(is_sinhala(c) for c in chars))
            self.assertEqual(len(set(chars)), len(chars))
        self.assertFalse(set(CONSONANTS) & set(INDEPENDENT_VOWELS))
        self.assertEqual(len(CONSONANTS), 41)
        self.assertEqual(len(INDEPENDENT_VOWELS), 18)

    def test_vowel_table_covers_every_vowel(self):
        self.assertEqual(set(VOWEL_TO_SIGN), set(INDEPENDENT_VOWELS))
        self.assertTrue(all(sign in VOWEL_SIGNS for sign in VOWEL_TO_SIGN.values() if sign))


if __name__ == '__main__':
    unittest.main()
