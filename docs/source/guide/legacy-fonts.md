# Old Sinhala fonts

Before Unicode, Sinhala was typed in fonts that show Sinhala letters in place of English ones.
If you copy text from a PDF or Word file that uses one of these fonts, you get gibberish such as
`jd;h` instead of `වාතය`. Many government documents and school textbooks still use them.

`from_legacy_font()` turns that text into proper Unicode Sinhala and cleans it up:

```python
>>> import sinling
>>> sinling.from_legacy_font('jd;h" c,h" wdydr')
'වාතය, ජලය, ආහාර'

>>> sinling.from_legacy_font("fomd\xbe;f\xefka;=j")
'දෙපාර්තමේන්තුව'

```

## Supported fonts

| `backend=` | Fonts |
| --- | --- |
| `fm` (default) | The FM fonts: FMAbhaya, FMMalithi, FMEmanee, FMAbabld and others with the same Wijesekara keyboard layout. |

Support for DL fonts and for old Tamil fonts such as Bamini is planned. The FM conversion was
tested on 2.8 million characters from 31 school textbooks.

## Convert only text in an old font

The converter turns English letters and punctuation into Sinhala, so normal English text would
be ruined. Text that is already in Unicode Sinhala is left unchanged.

In a PDF, convert only the parts typed in an FM font. `is_fm_font()` tells you whether a font
name is one of them, including the forms PDFs use, such as `ABCDEF+FMAbhaya`, and three FM
fonts whose names don't start with "FM":

```python
>>> from sinling.legacy_fonts import is_fm_font
>>> is_fm_font("ABCDEF+FMAbhaya"), is_fm_font("SARAWIPULA"), is_fm_font("Iskoola Pota")
(True, True, False)

```

## Characters it doesn't know

Characters the converter doesn't know are left as they are and counted in
`doc.meta["legacy_font_unmapped"]`, so you can see what's missing:

```python
>>> doc = sinling.pipeline(["legacy_font"])("jd;h\N{EURO SIGN}")
>>> doc.text, doc.meta["legacy_font_unmapped"]
('වාතය€', {'€': 1})

```

You can also find where each converted letter came from in the original text, even though the
font stores some vowel signs before their letter:

```python
>>> doc = sinling.pipeline(["legacy_font"])("frda.")
>>> doc.text, doc.raw[slice(*doc.to_raw(0, 2))]
('රෝග', 'frda')

```
