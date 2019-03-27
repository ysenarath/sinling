class Joiner:
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
                outputs.append(output_)
        return outputs
