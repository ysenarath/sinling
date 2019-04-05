__all__ = [
    'Joiner',
    'RuleBasedJoiner',
]


class Joiner:
    def join(self, l, r):
        raise NotImplementedError


class RuleBasedJoiner(Joiner):
    def __init__(self):
        self.rules = []

    def rule(self, func):
        self.rules.append(func)
        return func

    def join(self, l, r):
        outputs = []
        for rule in self.rules:
            output_ = rule(l, r)
            if output_ is not None:
                if isinstance(output_, (list, tuple)):
                    outputs += output_
                else:
                    outputs += [output_]
        return outputs
