from typing import Text, List

__all__ = [
    'Tokenizer'
]


# noinspection SpellCheckingInspection
class Tokenizer:
    def tokenize(self, sentence: Text) -> List[Text]:
        raise NotImplementedError()
