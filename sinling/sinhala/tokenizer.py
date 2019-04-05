import jnius_config

from sinling.config import BIN_PATH

__all__ = [
    'SinhalaTokenizer'
]


def import_class(class_):
    jnius_config.set_classpath(BIN_PATH)
    from jnius import autoclass
    return autoclass(class_)


class SinhalaTokenizer:
    __javaclass__ = 'SinhalaTokenizer'

    def __init__(self):
        self.tokenizer = import_class(SinhalaTokenizer.__javaclass__)()

    def contains_sinhala(self, text):
        return self.tokenizer.containsSinhala(text)

    def split_sentences(self, text):
        return self.tokenizer.splitSentences(text).toArray()

    def tokenize(self, text):
        return self.tokenizer.splitWords(text).toArray()


if __name__ == '__main__':
    doc = 'මට මං ගැනම ලොකු භයක් දැනෙනවා. සමහර වේලාවලට මට ජීවිතෙත් එපා වෙනවා.'
    tokenizer = SinhalaTokenizer()
    for sent in tokenizer.split_sentences(doc):
        for tok in tokenizer.tokenize(sent):
            print(tok, end=' ')
        print()
    assert tokenizer.contains_sinhala('ය')
