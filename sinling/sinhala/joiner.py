from sinling import utils
from sinling.core import RuleBasedJoiner
from sinling.sinhala import letters

__all__ = [
    'word_joiner'
]

word_joiner = RuleBasedJoiner()


@word_joiner.rule
def rule_0(l, r):
    """
    Rule for "Swạrạ"
    L[C1] + [V1]R → L[C1|V1]R
    :return:
    """
    c_suffix = utils.endswith(l, letters.CONSONANTS)
    if c_suffix is not None:
        c1 = c_suffix[0]
        lef = l[:-len(c_suffix)]
    else:
        return None
    v_prefix = utils.startswith(r, letters.VOWELS)
    if v_prefix:
        v2 = v_prefix
        rgt = r[len(v_prefix):]
    else:
        return None
    return lef + c1 + letters.DIACRITICS_MAPPING[v2] + rgt


@word_joiner.rule
def rule_1(l, r):
    """
    Rule for "Pūrwạ Swạrạ Lōpạ"
    L1[C1|V1] + [V2]R1 → L1[C1|V2]R1
    :return:
    """
    c_suffix = utils.endswith(l, letters.COMBINED_LETTERS)
    if c_suffix is not None:
        c1 = c_suffix[0]
        lef = l[:-len(c_suffix)]
    else:
        return None
    v_prefix = utils.startswith(r, letters.VOWELS)
    if v_prefix:
        v2 = v_prefix
        rgt = r[len(v_prefix):]
    else:
        return None
    return lef + c1 + letters.DIACRITICS_MAPPING[v2] + rgt


@word_joiner.rule
def rule_2(l, r):
    """
    Rule for "Parạ Swạrạ Lōpạ"
    TODO: Check whether this rule is correct
    L[C1|V1] + [V2]R → L[C1+V2]R
    :return:
    """
    c_suffix = utils.endswith(l, letters.COMBINED_LETTERS)
    if c_suffix is not None:
        c1 = c_suffix
        lef = l[:-len(c_suffix)]
    else:
        return None
    v_prefix = utils.startswith(r, letters.VOWELS)
    if v_prefix:
        rgt = r[len(v_prefix):]
    else:
        return None
    return lef + c1 + rgt


@word_joiner.rule
def rule_4(l, r):
    """
    Rule for "Swạrādeshạ"
    L[C1|​a] + [​i]R → L[C1|​e]R
    L[C1|​a] + [​u]R → L[C1|​o]R
    L[C1|​a] + [​u]R → L[C1|​ō]R
    L[C1|​e] + [​a]R → L[C1|​ā]R
    :return:
    """
    c_suffix = utils.endswith(l, letters.REVERSE_DIACRITICS_MAPPING)
    v_prefix = utils.startswith(r, letters.VOWELS)
    if c_suffix is not None and v_prefix is not None:
        rgt = r[len(v_prefix):]
        if letters.REVERSE_DIACRITICS_MAPPING[c_suffix] == 'අ':
            lef = l
            if v_prefix == 'ඉ':
                c1 = 'එ',
            elif v_prefix == 'උ':
                c1 = 'ඔ', 'ඕ'
            else:
                return None
        elif letters.REVERSE_DIACRITICS_MAPPING[c_suffix] == 'එ':
            lef = l[:-len(c_suffix)]
            if v_prefix == 'අ':
                c1 = 'ඈ',
            else:
                return None
        else:
            return None
    else:
        return None
    return [lef + letters.DIACRITICS_MAPPING[c2] + rgt for c2 in c1]


@word_joiner.rule
def rule_5(l, r):
    """
    Rule for "Gatrādeshạ"
    L[C1|V1] + [C2|V2]R → L[C1|V1][C3|V2]R; Where C3 is a member of {​y, v, h, k, t, p, n, m}
    :return:
    """
    lcom_suffix = utils.endswith(l, letters.COMBINED_LETTERS)
    l_suffix = utils.endswith(l, letters.REVERSE_DIACRITICS_MAPPING)
    v_suffix = letters.REVERSE_DIACRITICS_MAPPING[l_suffix]
    c_prefix = utils.startswith(r, letters.BASE_CONSONANTS)
    lft, rht = l, r
    outputs = []
    if v_suffix is not None and c_prefix == 'ක':
        rht = rht[len(c_prefix):]
        c_prefix = 'ය'
        outputs.append(lft + c_prefix + rht)
        c_prefix = 'ව'
        outputs.append(lft + c_prefix + rht)
    if lcom_suffix is not None:
        if lcom_suffix[0] == 'බ':
            lft = lft[:-len(lcom_suffix)]
            lcom_suffix = 'ප්'
            outputs.append(lft + lcom_suffix + rht)
        elif lcom_suffix[0] == 'ද':
            lft = lft[:-len(lcom_suffix)]
            lcom_suffix = 'ත්'
            outputs.append(lft + lcom_suffix + rht)
    return outputs


@word_joiner.rule
def rule_6(l, r):
    """
    Rule for "Pūrwạ Rūpạ"
    L[C1] + [C2|V2]R → L[C1][C1|V2]R
    :return:
    """
    lef, rgt = l, r
    c_suffix = utils.endswith(l, letters.COMBINED_LETTERS)
    rgt = rgt[1:]
    if c_suffix is not None:
        return lef + c_suffix[0] + rgt
    return None


@word_joiner.rule
def rule_7(l, r):
    """
    Rule for "Parạ Rūpạ"
    L[C1] + [C2|V2]R → L[C2][C2|V2]R
    :return:
    """
    lef, rgt = l, r
    r_prefix = utils.startswith(r, letters.COMBINED_LETTERS)
    l_suffix = utils.endswith(l, letters.COMBINED_LETTERS)
    if r_prefix is not None and l_suffix is not None:
        lef = lef[:-len(l_suffix)]
        l_suffix = r_prefix[0] + l_suffix[1:]
        return lef + l_suffix + rgt
    return None


@word_joiner.rule
def rule_8(l, r):
    """
    Rule for "Gatrākshạrạ Lōpạ"
    # todo: is this rule correct?
    L[ n ] + [C2|V2]R → L[ ňg |V2]R
    L[ n ] + [C2|V2]R → L[ ňb |V2]R
    :return:
    """
    lef, rgt = l, r
    l_suffix = utils.endswith(lef, letters.COMBINED_SAN)
    if l_suffix is not None:
        c1 = l_suffix[0]
        lef = lef[:-len(l_suffix)]
        l_suffix_san = letters.SAN_MAPPING[c1]
        lef += l_suffix_san[:-1]
        # r_prefix = utils.endswith(lef, letters.COMBINED_LETTERS)
        # v2 = r_prefix[1:]
        return lef + rgt
    return None


@word_joiner.rule
def rule_9(l, r):
    """
    Rule for "Āgạmạ"

    L[C1] + R → L[C1|u]R
    L[C1] + R → L[C1|i]R
    L[C1|V1] + [V2]R → L[C1|V1][C3|V2]R
    Where C3 = { y, v, r }
    :return:
    """
    lef, rgt = l, r
    l_suffix = utils.endswith(lef, letters.CONSONANTS)
    if l_suffix is not None:
        return [
            lef[:-len(l_suffix)] + l_suffix[0] + letters.DIACRITICS_MAPPING['උ'] + rgt,
            lef[:-len(l_suffix)] + l_suffix[0] + letters.DIACRITICS_MAPPING['ඉ'] + rgt,
        ]
    l_suffix = utils.endswith(lef, letters.COMBINED_LETTERS)
    r_prefix = utils.startswith(rgt, letters.VOWELS)
    if l_suffix is not None and r_prefix is not None:
        outputs = [lef + c3 + letters.DIACRITICS_MAPPING[r_prefix] + rgt[len(r_prefix):] for c3 in ['ව', 'ය', 'ර']]
        if len(l_suffix) > 1 and l_suffix[1] in letters.LONG_TO_SHORT_VOWEL_DIACRITICS_MAPPING:
            outputs.extend(
                [
                    lef[:-1] +
                    letters.LONG_TO_SHORT_VOWEL_DIACRITICS_MAPPING[l_suffix[1]] +
                    c3 +
                    letters.DIACRITICS_MAPPING[r_prefix] +
                    rgt[len(r_prefix):] for c3 in ['ව', 'ය', 'ර']
                ]
            )
        return outputs
    return None


@word_joiner.rule
def rule_10(l, r):
    """
    Rule for "Dwitwạ Rūpạ"

    L[C1|V1] + [V2]R → L[C1][C1|V2]R
    L[C1|V1] + [C1|V2]R → L[C1|v1][C1][C1|V2]R
    :return:
    """
    lef, rgt = l, r
    l_suffix = utils.endswith(lef, letters.COMBINED_LETTERS)
    r_prefix = utils.startswith(rgt, letters.VOWELS)
    if l_suffix is not None and r_prefix is not None:
        return lef[:-len(l_suffix)] + l_suffix[0] + '්' + l_suffix[0] + letters.DIACRITICS_MAPPING[r_prefix] + rgt[
                                                                                                             len(
                                                                                                                 r_prefix):]
    r_prefix = utils.startswith(rgt, letters.COMBINED_LETTERS)
    if l_suffix is not None and r_prefix is not None:
        return lef + r_prefix[0] + '්' + rgt
    return None


@word_joiner.rule
def rule_11(l, r):
    """
    Rule for "svara sandhi - svarṇa svara dīrghaya"

    :return:
    """
    l_suffix = utils.endswith(l, ['', 'ා'])
    r_prefix = utils.startswith(r, ['අ', 'ආ'])
    if l_suffix is not None and r_prefix is not None:
        if l_suffix == '':
            return l + 'ා' + r[len(r_prefix):]
        return l + r[len(r_prefix):]

    l_suffix = utils.endswith(l, ['ි', 'ී'])
    r_prefix = utils.startswith(r, ['ඉ', 'ඊ'])
    if l_suffix is not None and r_prefix is not None:
        return l[:-len(l_suffix)] + 'ී' + r[len(r_prefix):]

    l_suffix = utils.endswith(l, ['ු', 'ූ'])
    r_prefix = utils.startswith(r, ['උ', 'ඌ'])
    if l_suffix is not None and r_prefix is not None:
        return l[:-len(l_suffix)] + 'ූ' + r[len(r_prefix):]


@word_joiner.rule
def rule_12(l, r):
    """
    Rule for "svara sandhi - guṇa sandhiya"

    :return:
    """
    l_suffix = utils.endswith(l, ['', 'ා'])
    r_prefix = utils.startswith(r, ['ඉ', 'ඊ'])
    if l_suffix is not None:
        if r_prefix is not None:
            if l_suffix == '':
                return [l + v3 + r[len(r_prefix):] for v3 in ['ෙ', 'ේ']]
            return [l[:-len(l_suffix)] + v3 + r[len(r_prefix):] for v3 in ['ෙ', 'ේ']]

        # l_suffix = utils.endswith(l, ['', 'ා'])
        r_prefix = utils.startswith(r, ['උ', 'ඌ'])
        if r_prefix is not None:
            if l_suffix == '':
                return [l + v3 + r[len(r_prefix):] for v3 in ['ො', 'ෝ']]
            return [l[:-len(l_suffix)] + v3 + r[len(r_prefix):] for v3 in ['ො', 'ෝ']]

        # l_suffix = utils.endswith(l, ['', 'ා'])
        r_prefix = utils.startswith(r, ['ඍ'])
        if r_prefix is not None:
            if l_suffix == '':
                return l + 'ර්' + r[len(r_prefix):]
            return l[:-len(l_suffix)] + 'ර්' + r[len(r_prefix):]


@word_joiner.rule
def rule_13(l, r):
    """
    Rule for "svara sandhi - vṛddhi sandhiya"

    :return:
    """
    l_suffix = utils.endswith(l, ['', 'ා'])
    if l_suffix is not None:
        r_prefix = utils.startswith(r, ['එ'])
        if r_prefix is not None:
            if l_suffix == '':
                return l + 'ෛ' + r[len(r_prefix):]
            return l[:-len(l_suffix)] + 'ෛ' + r[len(r_prefix):]

        r_prefix = utils.startswith(r, ['ඔ'])
        if r_prefix is not None:
            if l_suffix == '':
                return l + 'ෞ' + r[len(r_prefix):]
            return l[:-len(l_suffix)] + 'ෞ' + r[len(r_prefix):]


@word_joiner.rule
def rule_14(l, r):
    """
    Rule for "svara sandhi - vṛddhi samāhāra sandhiya"

    :return:
    """
    l_suffix = utils.endswith(l, ['', 'ා'])
    if l_suffix is not None:
        r_prefix = utils.startswith(r, ['ඓ'])
        if r_prefix is not None:
            if l_suffix == '':
                return l + 'ෛ' + r[len(r_prefix):]
            return l[:-len(l_suffix)] + 'ෛ' + r[len(r_prefix):]

        r_prefix = utils.startswith(r, ['ඖ'])
        if r_prefix is not None:
            if l_suffix == '':
                return l + 'ෞ' + r[len(r_prefix):]
            return l[:-len(l_suffix)] + 'ෞ' + r[len(r_prefix):]


@word_joiner.rule
def rule_15(l, r):
    """
    Rule for "svara sandhi - ardha svara bhāva sandhiya"

    :return:
    """
    l_suffix = utils.endswith(l, ['ි', 'ී'])
    r_prefix = utils.startswith(r, ['අ', 'ආ', 'ඇ', 'ඈ', 'උ', 'ඌ', 'ඍ', 'ඎ', 'එ', 'ඒ', 'ඓ', 'ඔ', 'ඕ', 'ඖ'])
    if l_suffix is not None and r_prefix is not None:
        return l[:-len(l_suffix)] + '්‍ය' + letters.DIACRITICS_MAPPING[r_prefix] + r[len(r_prefix):]

    l_suffix = utils.endswith(l, ['ු', 'ූ'])
    r_prefix = utils.startswith(r, ['අ', 'ආ', 'ඇ', 'ඈ', 'ඉ', 'ඊ', 'ඍ', 'ඎ', 'එ', 'ඒ', 'ඓ', 'ඔ', 'ඕ', 'ඖ'])
    if l_suffix is not None and r_prefix is not None:
        return l[:-len(l_suffix)] + '්ව' + letters.DIACRITICS_MAPPING[r_prefix] + r[len(r_prefix):]

    l_suffix = utils.endswith(l, ['ෘ'])
    r_prefix = utils.startswith(r, ['අ', 'ආ', 'ඇ', 'ඈ', 'ඉ', 'ඊ', 'උ', 'ඌ', 'එ', 'ඒ', 'ඓ', 'ඔ', 'ඕ', 'ඖ'])
    if l_suffix is not None and r_prefix is not None:
        return l[:-len(l_suffix)] + '්‍ර' + letters.DIACRITICS_MAPPING[r_prefix] + r[len(r_prefix):]


@word_joiner.rule
def rule_16(l, r):
    """
    Rule for "vyaṁjana sandhi - ghośī karaṇaya"

    :return:
    """
    l_suffix = utils.endswith(l, letters.AGOSHA_LETTERS)
    r_prefix = utils.startswith(r, letters.GOSHA_LETTERS)
    if l_suffix is not None and r_prefix is not None:
        if r_prefix in letters.VOWELS:
            return l[:-len(l_suffix)] + letters.AGOSHA_TO_GOSHA_MAPPING[l_suffix][0] + \
                   letters.DIACRITICS_MAPPING[r_prefix] + r[len(r_prefix):]
        return l[:-len(l_suffix)] + letters.AGOSHA_TO_GOSHA_MAPPING[l_suffix] + r


@word_joiner.rule
def rule_17(l, r):
    """
    Rule for "vyaṁjana sandhi - talujikaraṇaya"

    :return:
    """
    l_suffix = utils.endswith(l, ['ත්'])
    r_prefix = utils.startswith(r, ['ච', 'ඡ', 'ජ', 'ඣ', 'ශ'])
    if l_suffix is not None and r_prefix is not None:
        if r_prefix == 'ශ':
            return l[:-len(l_suffix)] + 'ච්ඡ' + r[len(r_prefix):]
        return l[:-len(l_suffix)] + 'ච්' + r


@word_joiner.rule
def rule_18(l, r):
    """
    Rule for "vyaṁjana sandhi - pārśvīkaraṇaya"

    :return:
    """
    l_suffix = utils.endswith(l, ['ත්'])
    r_prefix = utils.startswith(r, ['ල'])
    if l_suffix is not None and r_prefix is not None:
        return l[:-len(l_suffix)] + 'ල්' + r


@word_joiner.rule
def rule_18(l, r):
    """
    Rule for "vyaṁjana sandhi - nāsikyakaraṇaya"

    :return:
    """
    l_suffix = utils.endswith(l, letters.AGOSHA_LETTERS)
    r_prefix = utils.startswith(r, ['ඞ', 'ඤ', 'ණ', 'න', 'ම'])
    if l_suffix is not None and r_prefix is not None:
        return l[:-len(l_suffix)] + letters.AGOSHA_TO_GOSHA_MAPPING[l_suffix] + r


@word_joiner.rule
def rule_18(l, r):
    """
    Rule for "vyaṁjana sandhi - dvitva rūpaya"

    :return:
    """
    l_suffix = utils.endswith(l, letters.VOWEL_DIACRITICS)
    r_prefix = utils.startswith(r, ['ඡ'])
    if l_suffix is not None and r_prefix is not None:
        return l + 'ච්' + r

