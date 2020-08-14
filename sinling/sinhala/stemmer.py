import os

import pygtrie as trie

from sinling.config import RESOURCE_PATH
from sinling.core import Stemmer

__all__ = [
    'SinhalaStemmer'
]


def _load_stem_dictionary():
    stem_dict = dict()
    with open(os.path.join(RESOURCE_PATH, 'stem_dictionary.txt'), 'r', encoding='utf-8') as fp:
        for line in fp.read().split('\n'):
            try:
                base, suffix = line.strip().split('\t')
                stem_dict[f'{base}{suffix}'] = (base, suffix)
            except ValueError as _:
                pass
    return stem_dict


def _load_suffixes():
    suffixes = trie.Trie()
    with open(os.path.join(RESOURCE_PATH, 'suffixes_list.txt'), 'r', encoding='utf-8') as fp:
        for suffix in fp.read().split('\n'):
            suffixes[suffix[::-1]] = suffix
    return suffixes


class SinhalaStemmer(Stemmer):
    def __init__(self):
        super().__init__()
        self.stem_dictionary = _load_stem_dictionary()
        self.suffixes = _load_suffixes()

    def stem(self, word):
        if word in self.stem_dictionary:
            return self.stem_dictionary[word]
        else:
            suffix = self.suffixes.longest_prefix(word[::-1]).key
            if suffix is not None:
                return word[0:-len(suffix)], word[len(word) - len(suffix):]
            else:
                return word, ''
