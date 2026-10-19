import os

import pygtrie as trie

from sinling.config import RESOURCE_PATH
from sinling.core import Stemmer

__all__ = [
    'SinhalaStemmer'
]


def _load_stem_dictionary():
    """Loads `stem_dictionary.txt`, one `word<TAB>stem` pair per line, as {word: (base, suffix)}.

    When the stem is not a prefix of the word (a spelling normalization, e.g. ඉන්දීය -> ඉන්දියාව),
    the stem is returned as the base with an empty suffix.
    """
    stem_dict = dict()
    with open(os.path.join(RESOURCE_PATH, 'stem_dictionary.txt'), 'r', encoding='utf-8') as fp:
        for line in fp.read().split('\n'):
            try:
                word, base = line.strip().split('\t')
            except ValueError as _:
                continue
            suffix = word[len(base):] if word.startswith(base) else ''
            stem_dict[word] = (base, suffix)
    return stem_dict


def _load_suffixes():
    suffixes = trie.Trie()
    with open(os.path.join(RESOURCE_PATH, 'suffixes_list.txt'), 'r', encoding='utf-8') as fp:
        for suffix in fp.read().split('\n'):
            suffixes[suffix[::-1]] = suffix
    return suffixes


class SinhalaStemmer(Stemmer):
    def __init__(self, use_dictionary=True):
        """
        :param use_dictionary: look words up in the stem dictionary before falling back to suffix stripping
        """
        super().__init__()
        self.stem_dictionary = _load_stem_dictionary() if use_dictionary else dict()
        self.suffixes = _load_suffixes()

    def stem(self, word):
        if word in self.stem_dictionary:
            return self.stem_dictionary[word]
        else:
            step = self.suffixes.longest_prefix(word[::-1])
            suffix = step.value if step else None
            if suffix and len(suffix) < len(word):  # never strip the whole word
                return word[0:-len(suffix)], word[len(word) - len(suffix):]
            else:
                return word, ''
