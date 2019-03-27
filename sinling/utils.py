def endswith(x, lst):
    for suffix in lst:
        if x.endswith(suffix):
            return suffix
    return None


def startswith(x, lst):
    for prefix in lst:
        if x.startswith(prefix):
            return prefix
    return None


def combine(cs, vs):
    return [ci + vi for ci in cs for vi in vs]
