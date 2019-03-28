from sinling import utils

CONSONANTS = [
    'ක', 'ඛ', 'ග', 'ඝ', 'ඞ', 'ඟ',
    'ච', 'ඡ', 'ජ', 'ඣ', 'ඤ', 'ඦ',
    'ට', 'ඨ', 'ඩ', 'ඪ', 'ණ', 'ඬ',
    'ත', 'ථ', 'ද', 'ධ', 'න', 'ඳ',
    'ප', 'ඵ', 'බ', 'භ', 'ම', 'ඹ',
    'ය', 'ර', 'ල', 'ව',
    'ශ', 'ෂ', 'ස', 'හ', 'ළ', 'ෆ',
]

SAN_MAPPING = {'ඟ': 'oග', 'ඦ': '', 'ඬ': '', 'ඳ': '', 'ඹ': 'ම්බ'}

BASE_CONSONANTS = [c + '්' for c in CONSONANTS]

VOWELS = [
    'අ', 'ආ', 'ඇ', 'ඈ', 'ඉ', 'ඊ', 'උ', 'ඌ',
    'ඍ', 'ඎ', 'එ', 'ඒ ', 'ඓ', 'ඔ', 'ඕ', 'ඖ',
    'අං', 'අඃ',
]

VOWEL_DIACRITICS = [
    '', 'ා', 'ැ', 'ෑ', 'ි', 'ී', 'ු', 'ූ', 'ෘ',
    'ෲ', 'ෙ', 'ේ', 'ෛ', 'ො', 'ෝ', 'ෞ',
    'ං', 'ඃ'
]

DIACRITICS_MAPPING = {v: d for v, d in zip(VOWELS, VOWEL_DIACRITICS)}

REVERSE_DIACRITICS_MAPPING = {d: v for v, d in zip(VOWELS, VOWEL_DIACRITICS)}

CONJUNCT_CONSONANTS = [
    'ක්ර', 'ඛ්ර', 'ග්ර', 'ඝ්ර', 'ඞ්ර', 'ඟ්ර',
    'ක්ය', 'ඛ්ය', 'ග්ය', 'ඝ්ය', 'ඞ්ය', 'ඟ්ය',
    'ක්ෂ', '෴',
]

NUMERALS = [
    '𑇡', '𑇢', '𑇣', '𑇤', '𑇥', '𑇦', '𑇧', '𑇨', '𑇩', '𑇪',
    '𑇫', '𑇬', '𑇭', '𑇮', '𑇯', '𑇰', '𑇱', '𑇲', '𑇳', '𑇴',
]

COMBINED_LETTERS = BASE_CONSONANTS + utils.combine(CONSONANTS, VOWEL_DIACRITICS)
