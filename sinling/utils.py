def endswith(x, lst):
    """ Select longest suffix that matches x from provided list(lst)

    :param x: input string
    :param lst: suffixes to compare with
    :return: longest suffix that matches input string if available otherwise None
    """
    longest_suffix = None
    for suffix in lst:
        if x.endswith(suffix):
            if longest_suffix is None or len(longest_suffix) < len(suffix):
                longest_suffix = suffix
    return longest_suffix


def startswith(x, lst):
    """ Select longest prefix that matches x from provided list(lst)

    :param x: input string
    :param lst: prefixes to compare with
    :return: longest prefix that matches input string if available otherwise None
    """
    longest_prefix = None
    for prefix in lst:
        if x.startswith(prefix):
            if longest_prefix is None or len(longest_prefix) < len(prefix):
                longest_prefix = prefix
    return longest_prefix


def combine(cs, vs):
    """ Returns all possible combinations preserving the order

    :param cs: list of first strings
    :param vs: list of second strings
    :return: list of combined strings
    """
    return [ci + vi for ci in cs for vi in vs]


def harmonic_mean(*a):
    return len(a) / sum([1 / k for k in a])
