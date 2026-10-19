import unittest

import sinling
from sinling import Doc, DocError, pipeline, sentences, tokenize

ZWJ = '\N{ZERO WIDTH JOINER}'
KOMBUVA = '\N{SINHALA VOWEL SIGN KOMBUVA}'


def kinds(text, **config):
    doc = pipeline([('tokenize', 'rules', config)])(text)
    return [(t.text, t.attrs['kind']) for t in doc.tokens]


class TokenizeTest(unittest.TestCase):
    def test_examples(self):
        examples = {
            'මම ගෙදර යනවා.': ['මම', 'ගෙදර', 'යනවා', '.'],
            'පෙ.ව. 10ට රු.500ක් ගෙවන්න.': ['පෙ.ව.', '10ට', 'රු.', '500ක්', 'ගෙවන්න', '.'],
            'ඒ.බී. පෙරේරා': ['ඒ.බී.', 'පෙරේරා'],
            f'ක්{ZWJ}රි.පූ. 250': [f'ක්{ZWJ}රි.පූ.', '250'],
            'ගව.': ['ගව', '.'],  # 0.3 kept the full stop: abbreviations now only start a word
            'රජ ඒ.': ['රජ', 'ඒ', '.'],  # ඒ ("that") is an abbreviation only in a chain such as ඒ.බී.
            'පා.ම. ඔහු': ['පා.ම.', 'ඔහු'],  # MP: a chain
            'අගය 3.14 යි, 1,000 ක්.': ['අගය', '3.14', 'යි', ',', '1,000', 'ක්', '.'],
            'මට වයස 10.': ['මට', 'වයස', '10', '.'],
            f'ශ්{ZWJ}රී ලංකාව': [f'ශ්{ZWJ}රී', 'ලංකාව'],
            'ඇත්තද?!...': ['ඇත්තද', '?', '!', '...'],
            '(වරහන්) "උද්ධෘත"': ['(', 'වරහන්', ')', '"', 'උද්ධෘත', '"'],
            'COVID-19 වසංගතය': ['COVID', '-', '19', 'වසංගතය'],
            '': [],
        }
        for text, expected in examples.items():
            with self.subTest(text=text):
                self.assertEqual(tokenize(text), expected)

    def test_kinds(self):
        text = ('බලන්න https://example.lk/a?b=1. yasas@example.com @user #ශ්' + ZWJ + 'රීලංකාව '
                '\N{THUMBS UP SIGN}\N{EMOJI MODIFIER FITZPATRICK TYPE-4} '
                '\N{MAN}' + ZWJ + '\N{WOMAN} රු.10 £5')
        self.assertEqual(kinds(text), [
            ('බලන්න', 'word'), ('https://example.lk/a?b=1', 'url'), ('.', 'punct'),
            ('yasas@example.com', 'email'), ('@user', 'mention'), ('#ශ්' + ZWJ + 'රීලංකාව', 'hashtag'),
            ('\N{THUMBS UP SIGN}\N{EMOJI MODIFIER FITZPATRICK TYPE-4}', 'emoji'),
            ('\N{MAN}' + ZWJ + '\N{WOMAN}', 'emoji'),
            ('රු.', 'abbreviation'), ('10', 'number'), ('£', 'symbol'), ('5', 'number'),
        ])

    def test_strings_are_normalized_first(self):
        self.assertEqual(tokenize(KOMBUVA + 'ගදර\N{NO-BREAK SPACE}යනවා'), ['ගෙදර', 'යනවා'])
        self.assertEqual(tokenize(KOMBUVA + 'ගදර', normalize=False), [KOMBUVA + 'ගදර'])

    def test_tokens_map_back_to_the_original(self):
        raw = '\N{ZERO WIDTH SPACE}' + KOMBUVA + 'ගදර යනවා'
        doc = pipeline(['normalize', 'tokenize'])(raw)
        self.assertEqual([doc.raw[slice(*doc.to_raw(t))] for t in doc.tokens], [KOMBUVA + 'ගදර', 'යනවා'])

    def test_combining_marks_stay_in_words(self):
        self.assertEqual(tokenize('cafe\N{COMBINING ACUTE ACCENT} ok', normalize=False),
                         ['cafe\N{COMBINING ACUTE ACCENT}', 'ok'])

    def test_text_is_never_changed(self):
        text = 'ÁÑé ගෙදර ©'  # 0.3 deleted these Latin-1 letters
        self.assertEqual(tokenize(text, normalize=False), ['ÁÑé', 'ගෙදර', '©'])

    def test_abbreviation_options(self):
        self.assertEqual(tokenize('ඩො. සිල්වා', extra_abbreviations=['ඩො.']), ['ඩො.', 'සිල්වා'])
        self.assertEqual(tokenize('රු.10', abbreviations=[]), ['රු', '.', '10'])
        self.assertEqual(tokenize('ඒ. පෙරේරා', chain_abbreviations=[]), ['ඒ', '.', 'පෙරේරා'])
        self.assertEqual(tokenize('ඒ.', abbreviations=['ඒ.']), ['ඒ.'])

    def test_registered(self):
        self.assertEqual([(b.task, b.name, b.default) for b in sinling.backends() if b.task in ('tokenize', 'sentences')],
                         [('sentences', 'rules', True), ('tokenize', 'rules', True)])


class SentencesTest(unittest.TestCase):
    def test_examples(self):
        examples = {
            'මම ගෙදර යනවා. ඔයා එනවද? එන්න!': ['මම ගෙදර යනවා.', 'ඔයා එනවද?', 'එන්න!'],
            'ඔහු කීවේ "මම එනවා." ඊට පසු ගියේය.': ['ඔහු කීවේ "මම එනවා."', 'ඊට පසු ගියේය.'],
            'පෙ.ව. 10ට එන්න. හරි.': ['පෙ.ව. 10ට එන්න.', 'හරි.'],
            'මට වයස 10. ඔයාට?': ['මට වයස 10.', 'ඔයාට?'],
            'ඉතින්... එහෙමද?!': ['ඉතින්...', 'එහෙමද?!'],
            'මම ගියෙමි \N{SINHALA PUNCTUATION KUNDDALIYA} ඔහු ආවේය \N{SINHALA PUNCTUATION KUNDDALIYA}':
                ['මම ගියෙමි \N{SINHALA PUNCTUATION KUNDDALIYA}', 'ඔහු ආවේය \N{SINHALA PUNCTUATION KUNDDALIYA}'],
            'ශීර්ෂය\n\nපළමු වාක්' + ZWJ + 'යය.': ['ශීර්ෂය', 'පළමු වාක්' + ZWJ + 'යය.'],
            '1. පළමු කරුණ\n2. දෙවන කරුණ': ['1. පළමු කරුණ', '2. දෙවන කරුණ'],
            '\N{BULLET} එක\n\N{BULLET} දෙක': ['\N{BULLET} එක', '\N{BULLET} දෙක'],
            'අවසන් තිතක් නැත': ['අවසන් තිතක් නැත'],
            '': [],
        }
        for text, expected in examples.items():
            with self.subTest(text=text):
                self.assertEqual(sentences(text), expected)

    def test_pipeline_sets_sentence_spans(self):
        doc = pipeline(['normalize', 'tokenize', 'sentences'])('මම යනවා. ඔයා එනවා.')
        self.assertEqual([(s.start, s.end) for s in doc.sents], [(0, 3), (3, 6)])
        self.assertEqual(doc.raw[slice(*doc.to_raw(doc.sents[1]))], 'ඔයා එනවා.')

    def test_needs_tokens(self):
        with self.assertRaisesRegex(DocError, 'tokenize'):
            pipeline(['sentences'])('මම යනවා.')

    def test_accepts_a_tokenized_doc(self):
        doc = pipeline(['tokenize'])('එක. දෙක.')
        self.assertEqual(sentences(doc), ['එක.', 'දෙක.'])
        self.assertEqual(len(doc.sents), 2)


if __name__ == '__main__':
    unittest.main()
