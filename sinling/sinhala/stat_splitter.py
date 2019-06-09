import os
import pickle
from statistics import harmonic_mean

from sinling.config import BIN_PATH
from sinling.core.splitter import Splitter

__all__ = [
    'word_splitter'
]


class CorpusBasedSplitter(Splitter):
    """ A very simple implementation of corpus based word splitter for splitting affixes from base word. """

    def __init__(self, path):
        """

        :param path:
        """
        super(CorpusBasedSplitter, self).__init__()
        with open(path, 'rb') as file:
            self.data = pickle.load(file)

    def split(self, text):
        """
        Splits the input text two two while trying to maximize the availability of parts in a defined corpus.

        :param text: input word
        :return: a dictionary containing `debug`, `base`, and `affix`.
        """
        debug = []
        max_score = 0
        best_split = None
        for i in range(1, len(text)):
            s1 = text[:i]
            s2 = text[i:]
            word_freq_s1 = self.data['dist'][s1]
            # Check base word (with ්) if s2 != ්
            if not s2.startswith('්'):
                s3 = text[:i] + '්'
                word_freq_s3 = self.data['dist'][s3]
                if word_freq_s3 > word_freq_s1:
                    word_freq_s1 = word_freq_s3
                    s1 = s3
            word_freq_s1 += 1
            count_words_ends_with_s2 = len([w for w in self.data['words'] if w.endswith(s2)]) + 1
            score = harmonic_mean([word_freq_s1, count_words_ends_with_s2])
            if score > max_score:
                max_score = score
                best_split = (s1, s2)
            debug.append([s1, s2, score])
        return {
            'debug': debug,
            'base': best_split[0],
            'affix': best_split[1],
        }


_data_path = os.path.join(BIN_PATH, 'stat.split.pickle')
if os.path.exists(_data_path):
    word_splitter = CorpusBasedSplitter(_data_path)
else:
    print(
        'Warning: splitter not initialized. '
        'Required data does not exist in `bin` folder. '
        'See the manual to how to download that data.'
    )
    word_splitter = Splitter()
