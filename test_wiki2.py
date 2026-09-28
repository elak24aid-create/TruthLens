import requests
import spacy
import re

nlp = spacy.load("en_core_web_sm")
headers = {'User-Agent': 'TruthLensBot/1.0'}

def get_wiki_summary(query):
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&utf8=&format=json"
        s_res = requests.get(search_url, headers=headers).json()
        search = s_res.get('query', {}).get('search', [])
        if not search:
            return ""
        title = search[0]['title']
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=true&explaintext=true&format=json&titles={title}"
        res = requests.get(url, headers=headers).json()
        pages = res.get('query', {}).get('pages', {})
        for page_id in pages:
            if str(page_id) != "-1":
                return pages[page_id].get('extract', '').lower()
    except Exception as e:
        print("Exception:", e)
    return ""

def check_identity(text):
    doc = nlp(text)
    be_verb = None
    for token in doc:
        if token.lemma_ == "be" and token.dep_ == "ROOT":
            be_verb = token
            break
    if not be_verb:
        return None
        
    subj_tokens = []
    attr_tokens = []
    for child in be_verb.children:
        if "subj" in child.dep_:
            subj_tokens = list(child.subtree)
        elif child.dep_ in ["attr", "acomp"]:
            attr_tokens = list(child.subtree)
            
    if subj_tokens and attr_tokens:
        subj = " ".join([t.text for t in subj_tokens]).strip()
        
        attr_core = None
        for t in attr_tokens:
            if t.dep_ in ["attr", "acomp"] and t.head == be_verb:
                attr_core = t.lemma_.lower()
                break
                
        if not attr_core:
            attr_core = attr_tokens[-1].lemma_.lower()
            
        summary = get_wiki_summary(subj)
        if not summary:
            return "No Wiki"
            
        # Exact word match
        if re.search(r'\b' + re.escape(attr_core) + r'\b', summary):
            return "SUPPORT"
        else:
            return "CONTRADICT"
            
    return None

claims = [
    "Michael Jackson is the president of the United States.", 
    "The Sun is a star.", 
    "The Earth is flat.", 
    "Donald Trump was the president of the United States.", 
    "Water is a liquid.", 
    "Elon Musk is the CEO of Tesla.",
    "2 + 2 = 5"
]
for c in claims:
    print(f"{c} -> {check_identity(c)}")
