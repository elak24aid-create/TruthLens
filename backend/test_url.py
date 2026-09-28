import urllib.request
from bs4 import BeautifulSoup
import spacy
import re

nlp = spacy.load("en_core_web_sm")

url = "https://en.wikipedia.org/wiki/Earth"
req = urllib.request.Request(url, headers={'User-Agent': 'TruthLens/1.0'})
html = urllib.request.urlopen(req).read()
soup = BeautifulSoup(html, 'html.parser')

for script in soup(["script", "style", "nav", "footer", "header", "aside", "table"]):
    script.decompose()

text = soup.get_text(separator=' ')
lines = (line.strip() for line in text.splitlines())
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
article_text = ' '.join(chunk for chunk in chunks if chunk)

doc = nlp(article_text[:2000])
for sent in doc.sents:
    # clean up citations [1]
    cleaned = re.sub(r'\[\d+\]', '', sent.text.strip())
    if len(cleaned.split()) > 5 and len(cleaned.split()) < 25:
        has_subj = any("subj" in token.dep_ for token in sent)
        has_verb = any(token.pos_ in ["VERB", "AUX"] for token in sent)
        if has_subj and has_verb:
            print("CLAIM FOUND:", cleaned)
            break
