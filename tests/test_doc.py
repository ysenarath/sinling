import json
import unittest

from sinling import Doc, DocError, Span, Token


class DocTextTest(unittest.TestCase):
    def test_new_doc_keeps_raw_text(self):
        doc = Doc('මම ගෙදර යනවා.')
        self.assertEqual(doc.raw, 'මම ගෙදර යනවා.')
        self.assertEqual(doc.text, doc.raw)
        self.assertEqual(doc.to_raw(3, 7), (3, 7))

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError):
            Doc(b'bytes')

    def test_edit_replaces_and_aligns(self):
        doc = Doc('abXYcd')
        doc.edit_text([(2, 4, 'Z')])
        self.assertEqual(doc.text, 'abZcd')
        self.assertEqual(doc.to_raw(2, 3), (2, 4))  # the replacement maps to what it replaced
        self.assertEqual(doc.to_raw(3, 5), (4, 6))
        self.assertEqual(doc.to_raw(0, 5), (0, 6))

    def test_deletion_keeps_neighbours_tight(self):
        doc = Doc('ab​cd')
        doc.edit_text([(2, 3, '')])
        self.assertEqual(doc.text, 'abcd')
        self.assertEqual(doc.to_raw(0, 2), (0, 2))  # ends before the deleted character
        self.assertEqual(doc.to_raw(2, 4), (3, 5))  # starts after it
        self.assertEqual(doc.to_raw(2, 2), (3, 3))

    def test_expansion_maps_every_part_to_the_source(self):
        doc = Doc('aXb')
        doc.edit_text([(1, 2, 'YZ')])
        self.assertEqual(doc.text, 'aYZb')
        self.assertEqual(doc.to_raw(1, 2), (1, 2))
        self.assertEqual(doc.to_raw(2, 3), (1, 2))

    def test_insertion(self):
        doc = Doc('ab')
        doc.edit_text([(1, 1, '-')])
        self.assertEqual(doc.text, 'a-b')
        self.assertEqual(doc.to_raw(2, 3), (1, 2))

    def test_edits_compose_across_calls(self):
        doc = Doc('a​b​c')
        doc.edit_text([(1, 2, ''), (3, 4, '')])
        doc.edit_text([(1, 2, 'BB')])
        self.assertEqual(doc.text, 'aBBc')
        self.assertEqual(doc.to_raw(1, 3), (2, 3))
        self.assertEqual(doc.to_raw(3, 4), (4, 5))
        self.assertEqual(doc.to_raw(0, 4), (0, 5))

    def test_unsorted_edits_are_applied_in_order(self):
        doc = Doc('abcd')
        doc.edit_text([(3, 4, 'D'), (0, 1, 'A')])
        self.assertEqual(doc.text, 'AbcD')

    def test_no_edits_leave_doc_unchanged(self):
        doc = Doc('abc')
        doc.edit_text([])
        self.assertEqual(doc.to_dict(), {'raw': 'abc', 'text': 'abc'})

    def test_overlapping_edits_are_rejected(self):
        doc = Doc('abcd')
        with self.assertRaises(DocError):
            doc.edit_text([(0, 2, 'x'), (1, 3, 'y')])
        self.assertEqual(doc.text, 'abcd')

    def test_out_of_range_edit_is_rejected(self):
        with self.assertRaises(DocError):
            Doc('ab').edit_text([(1, 5, '')])

    def test_text_is_fixed_after_tokenization(self):
        doc = Doc('ab')
        doc.set_tokens([Token('ab', 0, 2)])
        with self.assertRaises(DocError):
            doc.edit_text([(0, 1, 'A')])

    def test_to_raw_needs_valid_range(self):
        doc = Doc('ab')
        with self.assertRaises(DocError):
            doc.to_raw(1, 3)
        with self.assertRaises(TypeError):
            doc.to_raw(1)


class DocTokensTest(unittest.TestCase):
    def setUp(self):
        self.doc = Doc('මම  ගෙදර')
        self.doc.set_tokens([Token('මම', 0, 2), Token('ගෙදර', 4, 8)])

    def test_tokens_and_spans_map_to_text(self):
        self.assertTrue(self.doc.is_tokenized)
        self.assertEqual(self.doc.span_text(Span(0, 2)), 'මම  ගෙදර')
        self.assertEqual(self.doc.span_text(Span(1, 2)), 'ගෙදර')
        self.assertEqual(self.doc.to_raw(self.doc.tokens[1]), (4, 8))
        self.assertEqual(self.doc.to_raw(Span(0, 1)), (0, 2))

    def test_empty_span(self):
        self.assertEqual(self.doc.span_text(Span(2, 2)), '')

    def test_token_text_must_match(self):
        with self.assertRaises(DocError):
            Doc('abc').set_tokens([Token('x', 0, 1)])

    def test_tokens_must_not_overlap(self):
        with self.assertRaises(DocError):
            Doc('abc').set_tokens([Token('ab', 0, 2), Token('bc', 1, 3)])

    def test_span_outside_tokens(self):
        with self.assertRaises(DocError):
            self.doc.span_text(Span(1, 3))

    def test_tokens_after_normalization_map_to_raw(self):
        doc = Doc('ක​ර ගම')
        doc.edit_text([(1, 2, '')])
        doc.set_tokens([Token('කර', 0, 2), Token('ගම', 3, 5)])
        self.assertEqual(doc.to_raw(doc.tokens[0]), (0, 3))
        self.assertEqual(doc.to_raw(doc.tokens[1]), (4, 6))


class DocSerializationTest(unittest.TestCase):
    def test_round_trip_through_json(self):
        doc = Doc('ක​ර ගම')
        doc.edit_text([(1, 2, '')])
        doc.set_tokens([Token('කර', 0, 2, {'pos': 'VB'}), Token('ගම', 3, 5)])
        doc.sents = [Span(0, 2)]
        doc.spans['ents'] = [Span(1, 2, 'LOC', 0.9)]
        doc.meta['lang'] = 'si'
        data = json.loads(json.dumps(doc.to_dict(), ensure_ascii=False))
        copy = Doc.from_dict(data)
        self.assertEqual(copy.to_dict(), doc.to_dict())
        self.assertEqual(copy.to_raw(copy.tokens[1]), (4, 6))
        self.assertEqual(copy.spans['ents'][0].label, 'LOC')

    def test_changed_text_needs_alignment(self):
        with self.assertRaises(DocError):
            Doc.from_dict({'raw': 'ab', 'text': 'a'})

    def test_alignment_must_fit_text(self):
        with self.assertRaises(DocError):
            Doc.from_dict({'raw': 'ab', 'text': 'a', 'alignment': {'starts': [0], 'ends': [0]}})


if __name__ == '__main__':
    unittest.main()
