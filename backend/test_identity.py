import spacy
nlp = spacy.load('en_core_web_sm')
doc = nlp('The Sun is a star.')
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.dep_, token.head.text)
