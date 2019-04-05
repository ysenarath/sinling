import java.util.LinkedList;
import java.util.StringTokenizer;

public class SinhalaTokenizer {

    private LinkedList<String> ignoringCharList;

    private boolean isolatePunctuationsWithSpaces;

    private final String punctuationMarks[] = {".", ",", "\n", " ", "¸", "‚",
            "\"", "/", "-", "|", "\\", "—", "¦",
            "”", "‘", "'", "“", "’", "´", "´",
            "!", "@", "#", "$", "%", "^", "&", "\\*", "+", "\\-", "£", "\\?", "˜",
            "\\(", "\\)", "\\[", "\\]", "{", "}",
            ":", ";",
            "\u2013" /*EN-DASH*/
    };

    // these are invalid but separating 2 words. So, should be replaced by a space
    private final String invalidChars[] = {"Ê",
            "\u00a0", "\u2003", // spaces
            "\ufffd", "\uf020", "\uf073", "\uf06c", "\uf190", // unknown or invalid unicode chars
            "\u202a", "\u202c", "\u200f" //  direction control chars (for arabic, starting from right etc)
    };


    private final String wordTokenizerDelims;

    private final String lineTokenizingChars[] = {".", "?", "!", ":", ";", "\u2022"};

    private final String punctuationsWithoutLineTokenizingChars[] = {",", "¸", "‚",
            "\"", "/", "-", "\\|", "\\\\", "—", "¦",
            "”", "‘", "'", "“", "’", "´", "´",
            "!", "@", "#", "\\$", "\\%", "\\^", "\\&",
            "\\*", "\\+", "\\-", "£", "\\?", "˜",
            "\\(", "\\)", "\\[", "\\]", "\\{", "\\}",
            ":", ";",
            "\u2013"
    };

    private final String shortForms[] = {"ඒ\\.", "බී\\.", "සී\\.", "ඩී\\.", "ඊ\\.", "එෆ්\\.", "ජී\\.", "එච්\\.",
            "අයි\\.", "ජේ\\.", "කේ\\.", "එල්\\.", "එම්\\.", "එන්\\.", "ඕ\\.",
            "පී\\.", "කිව්\\.", "ආර්\\.", "එස්\\.", "ටී\\.", "යූ\\.", "ඩබ්\\.", "ඩබ්ලිව්\\.",
            "එක්ස්\\.", "වයි\\.", "ඉසෙඩ්\\.",
            "පෙ\\.", "ව\\.",
            "රු\\.",
            "පා\\.", // parliment
            "0\\.", "1\\.", "2\\.", "3\\.", "4\\.", "5\\.", "6\\.", "7\\.", "8\\.", "9\\."
    };

    private final String shortFormIdentifier = "\u0D80"; // this is an unassigned letter of sinhala block

    private final String lineTokenizerDelims;

    private void initIgnoringChars() {
        ignoringCharList.addLast("\u200c");
        ignoringCharList.addLast("\u0160");
        ignoringCharList.addLast("\u00ad");
        ignoringCharList.addLast("\u0088");
        ignoringCharList.addLast("\uf086");
        ignoringCharList.addLast("\u200b");
        ignoringCharList.addLast("\ufeff");
        ignoringCharList.addLast("Á");
        ignoringCharList.addLast("À");
        ignoringCharList.addLast("®");
        ignoringCharList.addLast("¡");
        ignoringCharList.addLast("ª");
        ignoringCharList.addLast("º");
        ignoringCharList.addLast("¤");
        ignoringCharList.addLast("¼");
        ignoringCharList.addLast("¾");
        ignoringCharList.addLast("Ó");
        ignoringCharList.addLast("ø");
        ignoringCharList.addLast("½");
        ignoringCharList.addLast("ˆ");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("¢");
        ignoringCharList.addLast("ÿ");
        ignoringCharList.addLast("·");
        ignoringCharList.addLast("í");
        ignoringCharList.addLast("Ω");
        ignoringCharList.addLast("°");
        ignoringCharList.addLast("×");
        ignoringCharList.addLast("µ");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("~");
        ignoringCharList.addLast("ƒ");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("ë");
        ignoringCharList.addLast("Î");
        ignoringCharList.addLast("‰");
        ignoringCharList.addLast("»");
        ignoringCharList.addLast("«");
        ignoringCharList.addLast("à");
        ignoringCharList.addLast("«");
        ignoringCharList.addLast("·");
        ignoringCharList.addLast("¨");
        ignoringCharList.addLast("…");
        ignoringCharList.addLast("⋆");
        ignoringCharList.addLast("›");
        ignoringCharList.addLast("¥");
        ignoringCharList.addLast("⋆");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("˝");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("◊");
        ignoringCharList.addLast("Ł");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("ê");
        ignoringCharList.addLast("Õ");
        ignoringCharList.addLast("Ä");
        ignoringCharList.addLast("á");
        ignoringCharList.addLast("Ñ");
        ignoringCharList.addLast("Í");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("Ñ");
        ignoringCharList.addLast("ç");
        ignoringCharList.addLast("Æ");
        ignoringCharList.addLast("ô");
        ignoringCharList.addLast("Ž");
        ignoringCharList.addLast("€");
        ignoringCharList.addLast("§");
        ignoringCharList.addLast("Æ");
        ignoringCharList.addLast("÷");
        ignoringCharList.addLast("é");
        ignoringCharList.addLast("¯");
        ignoringCharList.addLast("é");
        ignoringCharList.addLast("æ");
        ignoringCharList.addLast("î");
        ignoringCharList.addLast("ï");
        ignoringCharList.addLast("ä");
        ignoringCharList.addLast("Ô");
        ignoringCharList.addLast("õ");
        ignoringCharList.addLast("È");
        ignoringCharList.addLast("Ý");
        ignoringCharList.addLast("ß");
        ignoringCharList.addLast("õ");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("ù");
        ignoringCharList.addLast("å");
        ignoringCharList.addLast("Ø");
        ignoringCharList.addLast("Œ");
        ignoringCharList.addLast("Ô");
        ignoringCharList.addLast("Ü");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("Ö");
        ignoringCharList.addLast("Û");
        ignoringCharList.addLast("Ï");
        ignoringCharList.addLast("ñ");
        ignoringCharList.addLast("ý");
        ignoringCharList.addLast("œ");
        ignoringCharList.addLast("¹");
        ignoringCharList.addLast("");
        ignoringCharList.addLast("É");
        ignoringCharList.addLast("¯");
        ignoringCharList.addLast("Ò");
    }

    public SinhalaTokenizer() {
        isolatePunctuationsWithSpaces = false;

        for (String s : punctuationsWithoutLineTokenizingChars) {
            if (s.equals(shortFormIdentifier)) {
                System.out.println("Do not use " + shortFormIdentifier + " at punctuation list.");
                System.exit(-1);
            }
        }

        // init ignoring chars
        ignoringCharList = new LinkedList<String>();
        initIgnoringChars();

        // init word tokenizer
        String tmp = "[";
        for (String s : punctuationMarks) {
            tmp += s;
        }
        for (String s : invalidChars) {
            tmp += s;
        }

        tmp += "]";
        wordTokenizerDelims = tmp;

        // init line tokenizer
        tmp = "[";
        for (String s : lineTokenizingChars) {
            tmp += s;
        }
        tmp += "]";
        lineTokenizerDelims = tmp;
    }

    private void setIsolatePunctuationsWithSpaces(boolean state) {
        isolatePunctuationsWithSpaces = state;
    }

    public boolean isASinhalaLetter(String s) {
        if (s.length() != 1) return true;
        int sinhalaLowerBound = 3456;
        int sinhalaUpperBound = 3583;

        int cp = s.codePointAt(0);
        if (cp >= sinhalaLowerBound && cp <= sinhalaUpperBound) {
            return true;
        }
        return false;
    }


    public boolean containsSinhala(String s) {
        for (int i = 0; i < s.length(); ++i) {
            if (isASinhalaLetter(s.charAt(i) + "")) {
                return true;
            }
        }
        return false;
    }

    public LinkedList<String> splitWords(String str) {
        // remove ignoring chars from document
        for (String ignoringChar : ignoringCharList) {
            if (str.contains(ignoringChar)) {
                str = str.replaceAll(ignoringChar, "");
            }
        }

        LinkedList<String> list = new LinkedList<String>();

        StringTokenizer stringTokenizer = new StringTokenizer(str, wordTokenizerDelims, true);

        while (stringTokenizer.hasMoreTokens()) {
            list.add(stringTokenizer.nextToken());
        }
        return list;
    }

    public LinkedList<String> splitSentences(String str) {
        LinkedList<String> sentenceList = new LinkedList<String>();
        // remove ignoring chars from document
        for (String ignoringChar : ignoringCharList) {
            if (str.contains(ignoringChar)) {
                str = str.replaceAll(ignoringChar, "");
            }
        }

        // stop words being present with a punctuation at start or end of the word
        // Eg: word?     word,
        if (isolatePunctuationsWithSpaces) { // default is set to FALSE
            for (String punctuation : punctuationsWithoutLineTokenizingChars) {
                str = str.replaceAll(punctuation, " " + punctuation + " ");
            }
        }

        // prevent short froms being splitted into sentences
        // Eg: පෙ.ව.
        for (String shortForm : shortForms) {
            String representation = shortForm.substring(0, shortForm.length() - 1) + shortFormIdentifier;
            str = str.replaceAll(shortForm, representation);
        }

        //split lines
        String parts[] = str.split(lineTokenizerDelims);
        for (String sentence : parts) {
            sentence = sentence.replaceAll(shortFormIdentifier, ".");
            sentence = sentence.trim();

            if (containsSinhala(sentence)) {    // filter empty sentences and non-sinhala sentences
                sentenceList.addLast(sentence);
            }
        }
        return sentenceList;
    }

}