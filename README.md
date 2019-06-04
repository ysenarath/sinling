# SinLing
SinLing is to be the state of the art tool for Sinhalese Language Processing tasks. 

## How to get started
Steps-
1. Change dir path of your shell to project folder
1. Execute `javac bin/SinhalaTokenizer.java -encoding "UTF-8"` (you need to have Java JDK - tested with javac version 1.8.0_201)
1. Import required tools from the `sinling` module in your desired project 
(you may have to append this project path to your path environment variable)

## How to use
### Sinhala Tokenizer
```python
from sinling import SinhalaTokenizer

tokenizer = SinhalaTokenizer()

sentence = '...'  # your sentence

tokenizer.tokenize(sentence)
```

Sinhala tokenizer also includes `tokenizer.contains_sinhala(...)` and 
`tokenizer.split_sentences(...)` functions.

### Word Joiner (Morphological Joiner)
```python
from sinling import preprocess, word_joiner

w1 = preprocess('මුනි')
w2 = preprocess('උතුමා')
results = word_joiner.join(w1, w2)
# Returns a list of possible results after applying join rules ['මුනිතුමා', ...]
```

## Project Structure
```
project
.
+-- README.md 
+-- sinling
│   +-- ...
+--scripts
│   +-- rules_exmple.py
│   +-- evaluate.py
+--docs
    +-- existing_work
    │   +-- sinhala_alphabet.xls
    │   +-- helabasa
        │   +-- ...
```

## Contributions
- Contact `wayasas.13@cse.mrt.ac.lk` if you would like to contribute to this project.

## Special Notice
This project is still in work in progress status. Use at Your Own Risk.
