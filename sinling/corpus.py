class Field:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Corpus:
    def __init__(self, texts, *fields):
        self.texts = texts
        self.fields = {f.name: f for f in fields}
        self.values = {}
        for f in fields:
            self.values.update({f.name: self.fields[f.name].value(self)})

    def __getattr__(self, item):
        if item == 'texts':
            return self.texts
        elif item in self.fields:
            return self.values[item]
        else:
            return None


def field(name):
    def _decorated(func):
        return Field(name, func)

    return _decorated


@field('tokens')
def tokens(corpus):
    return [text.split(' ') for text in corpus.texts]


def main():
    text = 'This is a sample text'
    texts = [text]
    corpus = Corpus(texts, tokens)
    for txt, tok in zip(corpus.texts, corpus.tokens):
        print(txt, tok)


if __name__ == '__main__':
    main()
