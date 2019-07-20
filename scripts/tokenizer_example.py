from sinling import SinhalaTokenizer

if __name__ == '__main__':
    doc1 = 'මට මං ගැනම ලොකු භයක් දැනෙනවා. පෙ.ව. 5 වේලාවලට මට ජීවිතෙත් එපා වෙනවා. #gedaraEnawa'
    tokenizer = SinhalaTokenizer()
    for sent in tokenizer.split_sentences(doc1):
        for tok in tokenizer.tokenize(sent):
            print(tok, end=' ')
        print()
