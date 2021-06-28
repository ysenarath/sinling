# A language processing tool for Sinhalese (සිංහල). 

`Update 2020.11.01: Fixed pypi package. Use 'pip install sinling' to install sinling directly from repository.`

`Update 2020.08.16: Add pypi package @ https://pypi.org/project/sinling/.`

`Update 2020.08.16: Integrated Part of speech tagger and stemmer tool.`

`Update 2019.07.21: This tool no longer requires java to run sinhala tokenizer. 
All java code is ported to Python implementation for convenience.`

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ysenarath/sinling.git/master?filepath=notebooks%2Fexamples.ipynb)
[![PyPI version](https://badge.fury.io/py/sinling.svg)](https://badge.fury.io/py/sinling)

## Installation

Run the following command in your virtualenv to install this package.

`pip install sinling`

## How to use
### Sinhala Tokenizer
```python
from sinling import SinhalaTokenizer

tokenizer = SinhalaTokenizer()

sentence = '...'  # your sentence

tokenizer.tokenize(sentence)
```

### Sinhala Stemmer (Experimental)
```python
from sinling import SinhalaStemmer

stemmer = SinhalaStemmer()

word = '...'  # your sentence

stemmer.stem(word)
```

Please cite [sinhala-stemmer](https://github.com/rksk/sinhala-news-analysis/tree/master/sinhala-stemmer) if you are using this implementation.

### Part-of-Speech Tagger

```python
from sinling import SinhalaTokenizer, POSTagger

tokenizer = SinhalaTokenizer()

document = '...'  # may contain multiple sentences

tokenized_sentences = [tokenizer.tokenize(f'{ss}.') for ss in tokenizer.split_sentences(document)]

tagger = POSTagger()

pos_tags = tagger.predict(tokenized_sentences)
```

### Word Joiner (Morphological Joiner)
```python
from sinling import preprocess, word_joiner

w1 = preprocess('මුනි')
w2 = preprocess('උතුමා')
results = word_joiner.join(w1, w2)
# Returns a list of possible results after applying join rules ['මුනිතුමා', ...]
```

### Word Splitter (Morphological Splitter) / corpus based - *experimental*
```python
from sinling import word_splitter

word = '...'
results = word_splitter.split(word)
# Returns a dict containing debug information, base word and affix
```

Visit [here](https://github.com/ysenarath/sinling/blob/master/notebooks/splitter.ipynb) to see some sample splits.

## Contributions
- Contact `wayasas.13@cse.mrt.ac.lk` if you would like to contribute to this project.

## License
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
