from sinling import utils
from sinling.morph import Joiner
from sinling.sinhala import akuru

word_joiner = Joiner()


@word_joiner.rule
def rule_1(l, r):
    """
    Rule for "Pūrwạ Swạrạ Lōpạ"
    L1[C1|V1] + [V2]R1 → L1[C1|V2]R1
    :return:
    """
    c_suffix = utils.endswith(l, akuru.COMBINED_LETTERS)
    if c_suffix is not None:
        c1 = c_suffix[0]
        lef = l[:-len(c_suffix)]
    else:
        return None
    v_prefix = utils.startswith(r, akuru.VOWELS)
    if v_prefix:
        v2 = v_prefix
        rgt = r[len(v_prefix):]
    else:
        return None
    return lef + c1 + akuru.VOWEL_DIACRITICS_MAPPING[v2] + rgt


@word_joiner.rule
def rule_2(l, r):
    """
    Rule for "Parạ Swạrạ Lōpạ"
    TODO: Check whether this rule is correct
    L[C1|V1] + [V2]R → L[C1+V2]R
    :return:
    """
    lef, rgt = l[:-1], r[1:]
    c_suffix = utils.endswith(l, akuru.COMBINED_LETTERS)
    if c_suffix is not None:
        c1 = c_suffix[0]
    else:
        return None
    v_prefix = utils.startswith(r, akuru.VOWELS)
    if v_prefix:
        v2 = v_prefix
        rgt = r[len(v_prefix):]
    else:
        return None
    return lef + c1 + akuru.VOWEL_DIACRITICS_MAPPING[v2] + rgt
