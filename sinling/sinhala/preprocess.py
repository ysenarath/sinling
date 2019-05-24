__all__ = [
    'preprocess'
]


def fix_characters(text):
    text = text.replace('අා', 'ආ')
    text = text.replace('අැ', 'ඇ')
    text = text.replace('අෑ', 'ඈ')
    text = text.replace('උෘ', 'ඌ')
    return text


def preprocess(text, **options):
    x = text.strip()
    if 'fix_characters' not in options or ('fix_characters' in options and options['fix_characters']):
        x = fix_characters(x)
    return x
