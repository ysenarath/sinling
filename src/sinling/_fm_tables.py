"""Tables for the legacy FM Sinhala fonts (FMAbhaya, FMMalithi, FMEmanee, FMAbabld, ...).

Generated on 2026-10-18 from the SinhalaMMLU project's ``textbooks/fm_unicode.py``, where the
extended glyphs were read off the Educational Publications Department textbooks by context.
Keys are what a PDF extracts from FM-encoded text; values are Unicode. ``KOMBUVA`` is a
placeholder for the kombuva, which FM text stores before its consonant.
"""

KOMBUVA = '\ue000'

# Multi-character sequences, applied first (longest first)
SEQUENCES = {
    're': 'රු', 'rE': 'රූ', 'a/': '\u0dca\u200dරැ', 'a?': '\u0dca\u200dරෑ',
    '`o': 'ඳ', '`.': 'ඟ', '`v': 'ඬ', '`c': 'ඦ',
    '`': '', 'W!': 'ඌ', 'T!': 'ඖ', 'ft': 'ඓ',
}

# Single characters: the Wijesekara layout, moved punctuation, precomposed glyphs and symbols
CHARS = {
    'a': '\u0dca', 'A': '\u0dca', 'b': 'ඉ', 'B': 'ඊ', 'c': 'ජ', 'C': 'ක්',
    'd': '\u0dcf', 'D': '\u0dd8', 'e': '\u0dd0', 'E': '\u0dd1', 'f': '\ue000', 'F': 'ෆ',
    'g': 'ට', 'G': 'ඨ', 'h': 'ය', 'H': '\u0dca\u200dය', 'i': 'ස', 'I': 'ෂ',
    'j': 'ව', 'k': 'න', 'K': 'ණ', 'l': 'ක', 'L': 'ඛ', 'm': 'ප',
    'M': 'ඵ', 'n': 'බ', 'N': 'භ', 'o': 'ද', 'O': 'ධ', 'p': 'ච',
    'P': 'ඡ', 'q': '\u0dd4', 'Q': '\u0dd6', 'r': 'ර', 'R': 'ඍ', 's': '\u0dd2',
    'S': '\u0dd3', 't': 'එ', 'T': 'ඔ', 'u': 'ම', 'U': 'ඹ', 'v': 'ඩ',
    'V': 'ඪ', 'w': 'අ', 'W': 'උ', 'x': '\u0d82', 'X': 'ඞ', 'y': 'හ',
    'Y': 'ශ', 'z': '‘', 'Z': '’', ';': 'ත', ':': 'ථ', ',': 'ල',
    '<': 'ළ', '.': 'ග', '>': 'ඝ', '/': 'රැ', '?': 'රෑ', '[': 'ඤ',
    '{': 'ඥ', '|': 'ඳ', '=': '\u0dd4', '+': '\u0dd6', '!': '\u0ddf', '%': '\u0dca\u200dර',
    '*': 'ෆ', '\'': '.', '"': ',', '^': '(', '&': ')', '(': ':',
    '$': '/', '@': '?', ']': '%', '\xe6': '!', '\xa6': '.', '\xa1': '-',
    '#': '\'', '\xbe': 'ර්', '\xfa': 'වි', '\xf9': 'වී', '\xf5': 'ව්', '\xef': 'ම්',
    '\xf1': 'මි', '\xf3': 'මී', '\xf8': 'ද්\u200dර', '\xdf': 'රි', '\xcd': 'රී', '\xc8': 'දි',
    '\xa7': 'දී', '\xff': 'දු', '\xa5': 'දූ', '\xb1': 'දැ', '\xde': 'දා', '\xe1': 'ටි',
    '\xe0': 'ටී', '\xdc': 'ට්', '\xc0': 'ටි', '\xe4': 'ඩි', '\xe3': 'ඩී', '\xe2': 'ඩ්',
    '\xec': 'බි', '\xee': 'බී', '\xed': 'බ්', '\xcb': 'බ්ධ', '\xea': 'ධි', '\xeb': 'ධී',
    '\xe8': 'ධ්', '\xd4': 'ජී', '\xf0': 'ජි', '\xca': 'ජ්', '\xd1': 'චි', '\xd6': 'චී',
    '\xc9': 'ච්', '\xd3': 'ථි', '\xd2': 'ථි', '\xc1': 'ඨි', '\xa2': 'ඳි', '\xf7': 'ඳු',
    '\xaa': 'ඳු', '\xa8': 'ලු', '\xc6': 'ලූ', '\xbf': 'ළු', '\xf4': 'ඹි', '\xf6': 'ඹී',
    '\xa3': 'ඹු', '\xb4': 'ඕ', '\u201a': 'ණි', '\xd5': 'ඟ', '\xfe': 'ඡ', '~': 'ඬ',
    '\xe5': 'ඬ', '\xe7': 'ඬි', '\xf2': 'ඹ්', '\u0152': 'ණී', '\xce': 'ණි', '\xc5': 'ඛි',
    '\xc7': 'ඛී', '\xc4': 'ඛ', '\xd7': 'ඥා', '\xae': 'ඣ', '\xb5': 'ද්\u200dය', '\xfd': 'ඡි',
    '\xd8': 'ඤ', '\xd9': 'ඞ්', '\xb8': 'i', '\xb9': 'v', '\xba': 'x', '\xbb': 'i',
    '\u2122': '“', '\u0161': '”', '\u25cf': '•', '\u25e6': '•', '\xb2': '•', '\xb3': '•',
    '\u2022': '•', '\xac': '→', '\xab': '', '}': '', '\u201d': '', '\u2014': '“',
    '\u02dc': '”',
}

# Independent vowel + sign drawn as one vowel letter in FM fonts
INDEPENDENT_VOWELS = {
    '\u0d85\u0dcf': 'ආ', '\u0d85\u0dd0': 'ඇ', '\u0d85\u0dd1': 'ඈ', '\u0d91\u0dca': 'ඒ',
    '\u0d94\u0dca': 'ඕ', '\u0d8b\u0ddf': 'ඌ', '\u0d94\u0ddf': 'ඖ',
}
