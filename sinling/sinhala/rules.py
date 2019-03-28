from sinling import utils
from sinling.core import Joiner
from sinling.sinhala import akuru

word_joiner = Joiner()


@word_joiner.rule
def rule_0(l, r):
    """
    Rule for "Swạrạ"
    L[C1] + [V1]R → L[C1|V1]R
    :return:
    """
    c_suffix = utils.endswith(l, akuru.BASE_CONSONANTS)
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
    return lef + c1 + akuru.DIACRITICS_MAPPING[v2] + rgt


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
    return lef + c1 + akuru.DIACRITICS_MAPPING[v2] + rgt


@word_joiner.rule
def rule_2(l, r):
    """
    Rule for "Parạ Swạrạ Lōpạ"
    TODO: Check whether this rule is correct
    L[C1|V1] + [V2]R → L[C1+V2]R
    :return:
    """
    c_suffix = utils.endswith(l, akuru.COMBINED_LETTERS)
    if c_suffix is not None:
        c1 = c_suffix
        lef = l[:-len(c_suffix)]
    else:
        return None
    v_prefix = utils.startswith(r, akuru.VOWELS)
    if v_prefix:
        rgt = r[len(v_prefix):]
    else:
        return None
    return lef + c1 + rgt


@word_joiner.rule
def rule_4(l, r):
    """
    Rule for "Swạrādeshạ"
    TODO: Check whether this rule is correct
    L[C1|​a] + [​i]R → L[C1|​e]R
    L[C1|​a] + [​u]R → L[C1|​o]R
    L[C1|​a] + [​u]R → L[C1|​ō]R
    :return:
    """
    lef = l
    c_suffix = utils.endswith(l, akuru.REVERSE_DIACRITICS_MAPPING)
    if c_suffix is not None and akuru.REVERSE_DIACRITICS_MAPPING[c_suffix] == 'අ':
        pass
    else:
        return None
    v_prefix = utils.startswith(r, akuru.VOWELS)
    if v_prefix is not None:
        if v_prefix == 'ඉ':
            c1 = 'එ',
            rgt = r[len(v_prefix):]
        elif v_prefix == 'උ':
            c1 = 'ඔ', 'ඕ'
            rgt = r[len(v_prefix):]
        else:
            return None
    else:
        return None
    return [lef + akuru.DIACRITICS_MAPPING[c2] + rgt for c2 in c1]
