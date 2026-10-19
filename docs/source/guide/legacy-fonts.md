# Legacy fonts

Before Unicode was common, Sinhala was typed in fonts that draw Sinhala letters on Latin
characters. Text extracted from a PDF or Word file that uses such a font reads as gibberish:
`jd;h` instead of `වාතය`. Many government documents and school textbooks still use them.

`from_legacy_font()` converts that text to Unicode, then normalizes it:

```python
>>> import sinling
>>> sinling.from_legacy_font('jd;h" c,h" wdydr')
'වාතය, ජලය, ආහාර'

>>> sinling.from_legacy_font("fomd\xbe;f\xefka;=j")
'දෙපාර්තමේන්තුව'

```

## Supported fonts

| Backend | Fonts |
| --- | --- |
| `fm` (default) | The FM family: FMAbhaya, FMMalithi, FMEmanee, FMAbabld and others that share the Wijesekara layout. |

DL fonts and Tamil legacy fonts such as Bamini are planned.

The `fm` tables were built from the Educational Publications Department textbooks. On 2.8
million characters of text extracted from 31 of them, the output matched the converter it was
ported from exactly.

## Only convert legacy-font text

The converter remaps Latin letters and punctuation, so ordinary English or Unicode-font text
would be garbled. In a PDF, convert only the spans whose font is a legacy font.
`is_fm_font()` recognizes FM fonts by name, including subset prefixes and three FM-encoded fonts
whose names don't start with "FM":

```python
>>> from sinling.legacy_fonts import is_fm_font
>>> is_fm_font("ABCDEF+FMAbhaya"), is_fm_font("SARAWIPULA"), is_fm_font("Iskoola Pota")
(True, True, False)

```

Unicode Sinhala passes through unchanged, so a span that is already Unicode is safe.

## Gaps and offsets

Characters the converter has no mapping for are kept and counted in
`doc.meta["legacy_font_unmapped"]`, which helps find gaps in the tables:

```python
>>> doc = sinling.pipeline(["legacy_font"])("jd;h\N{EURO SIGN}")
>>> doc.text, doc.meta["legacy_font_unmapped"]
('වාතය€', {'€': 1})

```

Every converted character maps back to the extracted text, including vowel signs that the
font stores before their consonant:

```python
>>> doc = sinling.pipeline(["legacy_font"])("frda.")
>>> doc.text, doc.raw[slice(*doc.to_raw(0, 2))]
('රෝග', 'frda')

```
