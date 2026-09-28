from app.services.online_research import *

doc = nlp('The Sun is a star.')
be_verb = None
for token in doc:
    if token.lemma_ == "be" and token.dep_ == "ROOT":
        be_verb = token
        break
print("be_verb:", be_verb)
subj_tokens = []
attr_tokens = []
for child in be_verb.children:
    print(child.text, child.dep_)
    if "subj" in child.dep_:
        subj_tokens = list(child.subtree)
    elif child.dep_ in ["attr", "acomp"]:
        attr_tokens = list(child.subtree)
        
print("Subj_tokens:", [t.text for t in subj_tokens])
# Notice the list comprehension inside the join. 
# In online_research.py: subj = " ".join([t.text for t in subj_tokens if t.pos_ in ["NOUN", "PROPN"]]).strip()
subj = " ".join([t.text for t in subj_tokens if t.pos_ in ["NOUN", "PROPN"]]).strip()
print("Subj:", subj)

attr_lemmas = [t.lemma_.lower() for t in attr_tokens if not t.is_stop and t.is_alpha]
print("Attr lemmas:", attr_lemmas)
