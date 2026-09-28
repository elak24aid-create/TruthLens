import spacy

nlp = spacy.load("en_core_web_sm")

def extract_identity_claim(text):
    doc = nlp(text)
    
    # Find the main 'be' verb
    be_verb = None
    for token in doc:
        if token.lemma_ == "be" and token.dep_ == "ROOT":
            be_verb = token
            break
            
    if not be_verb:
        return None
        
    subject_tokens = []
    attr_tokens = []
    
    for child in be_verb.children:
        if "subj" in child.dep_:
            subject_tokens = list(child.subtree)
        elif child.dep_ in ["attr", "acomp"]:
            attr_tokens = list(child.subtree)
            
    if subject_tokens and attr_tokens:
        subj = " ".join([t.text for t in subject_tokens]).strip()
        attr = " ".join([t.text for t in attr_tokens]).strip()
        return subj, attr
    return None

claims = [
    "Michael Jackson is the president of the United States.",
    "The Sun is a star.",
    "The Earth is flat.",
    "Donald Trump was the president of the United States.",
    "Water is a liquid.",
    "Elon Musk is the CEO of Tesla."
]

for c in claims:
    print(f"{c} -> {extract_identity_claim(c)}")
