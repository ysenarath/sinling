import re

__all__ = [
    'SinhalaTokenizer'
]


def is_a_sinhala_letter(s: str) -> bool:
    if len(s) != 1:
        return True
    sinhala_lower_bound = 3456
    sinhala_upper_bound = 3583
    cp = ord(s[0])  # first letter of str
    if sinhala_lower_bound <= cp <= sinhala_upper_bound:
        return True
    return False


def contains_sinhala(s: str) -> bool:
    for c in s:
        if is_a_sinhala_letter(c):
            return True
    return False


class Tokenizer:
    def tokenize(self, sentence):
        raise NotImplementedError()


class SinhalaTokenizer(Tokenizer):
    def __init__(self):
        self.ignoring_chars: list = []
        self.isolate_punctuations_with_spaces: bool = False
        self.punctuation_marks: list = [
            ".", ",", "\n", " ", "¸", "‚",
            "\"", "/", "-", "|", "\\", "—", "¦",
            "”", "‘", "'", "“", "’", "´", "´",
            "!", "@", "#", "$", "%", "^", "&", "\\*", "+", "\\-", "£", "\\?", "˜",
            "\\(", "\\)", "\\[", "\\]", "{", "}",
            ":", ";",
            "\u2013"  # EN - DASH
        ]
        self.invalid_chars: list = [
            "Ê",
            "\u00a0", "\u2003",  # spaces
            "\ufffd", "\uf020", "\uf073", "\uf06c", "\uf190",  # unknown or invalid unicode chars
            "\u202a", "\u202c", "\u200f"  # direction control chars(for arabic, starting from right etc)
        ]
        self.word_tokenizer_delims: str = ""
        self.line_tokenizing_chars: list = [
            ".", "?", "!", ":", ";", "\u2022"
        ]
        self.punctuations_without_line_tokenizing_chars: list = [
            ",", "¸", "‚",
            "\"", "/", "-", "\\|", "\\\\", "—", "¦",
            "”", "‘", "'", "“", "’", "´", "´",
            "!", "@", "#", "\\$", "\\%", "\\^", "\\&",
            "\\*", "\\+", "\\-", "£", "\\?", "˜",
            "\\(", "\\)", "\\[", "\\]", "\\{", "\\}",
            ":", ";",
            "\u2013"
        ]
        self.short_forms: list = [
            "ඒ.", "බී.", "සී.", "ඩී.", "ඊ.", "එෆ්.", "ජී.", "එච්.",
            "අයි.", "ජේ.", "කේ.", "එල්.", "එම්.", "එන්.", "ඕ.",
            "පී.", "කිව්.", "ආර්.", "එස්.", "ටී.", "ය.", "ඩබ.", "ඩබ්ලිව්.",
            "එක්ස්.", "වයි.", "ඉසෙඩ්.",
            "පෙ.", "ව.",
            "රු.",
            "පා.",  # parliment
            "0.", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."
        ]
        self.short_form_identifier: str = "\u0D80"
        self.line_tokenizer_delims: str = ""

        for s in self.punctuations_without_line_tokenizing_chars:
            if self.short_form_identifier == s:
                print("Do not use " + self.short_form_identifier + " at punctuation list.")

        #  init ignoring chars
        self._init_ignoring_chars()

        # init word tokenizer
        tmp = "["
        for s in self.punctuation_marks:
            tmp += s
        for s in self.invalid_chars:
            tmp += s
        tmp += "]"
        self.word_tokenizer_delims = tmp

        # init line tokenizer
        tmp = "["
        for s in self.line_tokenizing_chars:
            tmp += s
        tmp += "]"
        self.line_tokenizer_delims = tmp

    def set_isolate_punctuations_with_spaces(self, state: bool):
        self.isolate_punctuations_with_spaces = state

    def _init_ignoring_chars(self):
        self.ignoring_chars.append("\u200c")
        self.ignoring_chars.append("\u0160")
        self.ignoring_chars.append("\u00ad")
        self.ignoring_chars.append("\u0088")
        self.ignoring_chars.append("\uf086")
        self.ignoring_chars.append("\u200b")
        self.ignoring_chars.append("\ufeff")
        self.ignoring_chars.append("Á")
        self.ignoring_chars.append("À")
        self.ignoring_chars.append("®")
        self.ignoring_chars.append("¡")
        self.ignoring_chars.append("ª")
        self.ignoring_chars.append("º")
        self.ignoring_chars.append("¤")
        self.ignoring_chars.append("¼")
        self.ignoring_chars.append("¾")
        self.ignoring_chars.append("Ó")
        self.ignoring_chars.append("ø")
        self.ignoring_chars.append("½")
        self.ignoring_chars.append("ˆ")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("¢")
        self.ignoring_chars.append("ÿ")
        self.ignoring_chars.append("·")
        self.ignoring_chars.append("í")
        self.ignoring_chars.append("Ω")
        self.ignoring_chars.append("°")
        self.ignoring_chars.append("×")
        self.ignoring_chars.append("µ")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("~")
        self.ignoring_chars.append("ƒ")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("ë")
        self.ignoring_chars.append("Î")
        self.ignoring_chars.append("‰")
        self.ignoring_chars.append("»")
        self.ignoring_chars.append("«")
        self.ignoring_chars.append("à")
        self.ignoring_chars.append("«")
        self.ignoring_chars.append("·")
        self.ignoring_chars.append("¨")
        self.ignoring_chars.append("…")
        self.ignoring_chars.append("⋆")
        self.ignoring_chars.append("›")
        self.ignoring_chars.append("¥")
        self.ignoring_chars.append("⋆")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("˝")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("◊")
        self.ignoring_chars.append("Ł")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("ê")
        self.ignoring_chars.append("Õ")
        self.ignoring_chars.append("Ä")
        self.ignoring_chars.append("á")
        self.ignoring_chars.append("Ñ")
        self.ignoring_chars.append("Í")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("Ñ")
        self.ignoring_chars.append("ç")
        self.ignoring_chars.append("Æ")
        self.ignoring_chars.append("ô")
        self.ignoring_chars.append("Ž")
        self.ignoring_chars.append("€")
        self.ignoring_chars.append("§")
        self.ignoring_chars.append("Æ")
        self.ignoring_chars.append("÷")
        self.ignoring_chars.append("é")
        self.ignoring_chars.append("¯")
        self.ignoring_chars.append("é")
        self.ignoring_chars.append("æ")
        self.ignoring_chars.append("î")
        self.ignoring_chars.append("ï")
        self.ignoring_chars.append("ä")
        self.ignoring_chars.append("Ô")
        self.ignoring_chars.append("õ")
        self.ignoring_chars.append("È")
        self.ignoring_chars.append("Ý")
        self.ignoring_chars.append("ß")
        self.ignoring_chars.append("õ")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("ù")
        self.ignoring_chars.append("å")
        self.ignoring_chars.append("Ø")
        self.ignoring_chars.append("Œ")
        self.ignoring_chars.append("Ô")
        self.ignoring_chars.append("Ü")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("Ö")
        self.ignoring_chars.append("Û")
        self.ignoring_chars.append("Ï")
        self.ignoring_chars.append("ñ")
        self.ignoring_chars.append("ý")
        self.ignoring_chars.append("œ")
        self.ignoring_chars.append("¹")
        self.ignoring_chars.append("")
        self.ignoring_chars.append("É")
        self.ignoring_chars.append("¯")
        self.ignoring_chars.append("Ò")

    def tokenize(self, s: str) -> list:
        # remove ignoring chars from document
        for ignoring_char in self.ignoring_chars:
            if ignoring_char in s:
                s = s.replace(ignoring_char, "")

        # prevent short forms being splitted into separate tokens
        # Eg: පෙ.ව.
        for short_form in self.short_forms:
            representation = short_form[0:len(short_form) - 1] + self.short_form_identifier
            s = s.replace(short_form, representation)

        parts = re.split(r'({})'.format(self.word_tokenizer_delims), s)
        tokens = []
        for token in parts:
            token = token.replace(self.short_form_identifier, ".")
            tokens.append(token)
        return tokens

    def split_sentences(self, doc: str) -> list:
        # remove ignoring chars from document
        for ignoring_char in self.ignoring_chars:
            if ignoring_char in doc:
                doc = doc.replace(ignoring_char, "")

        # stop words being present with a punctuation at start or end of the word
        # Eg: word?     word,
        if self.isolate_punctuations_with_spaces:  # default is set to FALSE
            for punctuation in self.punctuations_without_line_tokenizing_chars:
                doc = doc.replace(punctuation, " " + punctuation + " ")

        # prevent short forms being splitted into sentences
        # Eg: පෙ.ව.
        for short_form in self.short_forms:
            representation = short_form[0:len(short_form) - 1] + self.short_form_identifier
            doc = doc.replace(short_form, representation)

        sentences = []
        # split lines
        parts = re.split(r"{}".format(self.line_tokenizer_delims), doc)
        for sentence in parts:
            sentence = sentence.replace(self.short_form_identifier, ".")
            sentence = sentence.strip()
            if contains_sinhala(sentence):  # filter empty sentences and non-sinhala sentences
                sentences.append(sentence)
        return sentences
