import spacy
nlp = spacy.load("en_core_web_sm")
text = """Subscribe to our newsletter for more updates. Earth is the third planet from the Sun and the only astronomical object known to harbor life. Please accept our cookies."""
doc = nlp(text)
for sent in doc.sents:
    ents = len(sent.ents)
    has_subj = any("subj" in t.dep_ for t in sent)
    print(sent.text.strip(), ents, has_subj)
