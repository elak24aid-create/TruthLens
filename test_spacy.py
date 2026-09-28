import spacy
nlp = spacy.load("en_core_web_sm")
claims = [
    "Michael Jackson is the president of the United States.",
    "The Sun is a star.",
    "The Earth is flat.",
    "2 + 2 = 5.",
    "Water freezes at 0 degrees Celsius at standard atmospheric pressure."
]
for c in claims:
    print(f"\n--- {c} ---")
    doc = nlp(c)
    for token in doc:
        print(f"{token.text:15} {token.lemma_:15} {token.pos_:10} {token.dep_}")
