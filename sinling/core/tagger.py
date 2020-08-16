from typing import List, Text, Tuple

__all__ = ['Tagger']


class Tagger:
    def predict(self, tokens: List[Text]) -> List[Tuple[Text, Text]]:
        raise NotImplementedError
