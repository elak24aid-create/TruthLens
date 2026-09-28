import re

with open("backend/app/services/url_extractor.py", "r") as f:
    c = f.read()

new_claim = """    # Formulate claim text for searching
    clean_title = re.split(r'[-|]', title)[0].strip()
    claim_text = clean_title
    if len(claim_text) < 40 and description:
        claim_text += ' ' + description
        
    claim_text = claim_text[:80].strip()
    if not claim_text:
        claim_text = title[:80]
"""

c = re.sub(r'# Formulate claim text for searching.*?if len\(claim_text\) > 150:\s*claim_text = claim_text\[:147\] \+ "\.\.\."', new_claim, c, flags=re.DOTALL)

with open("backend/app/services/url_extractor.py", "w") as f:
    f.write(c)
