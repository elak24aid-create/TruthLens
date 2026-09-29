import requests, time

claims = [
    ('The Amazon River flows through Brazil.', 'geography'),
    ('The chemical symbol for gold is Au.', 'science'),
    ('Light travels faster than sound.', 'science'),
    ('The Nile River is located in South America.', 'geography'),
    ('Australia is the smallest continent.', 'geography'),
    ('Python is a programming language.', 'technology'),
    ('Napoleon Bonaparte was born in France.', 'history'),
    ('William Shakespeare was a 20th-century playwright.', 'person_identity'),
    ('The United States declared independence in 1776.', 'dates'),
    ('Greenhouse gas emissions contribute to global warming.', 'cause_effect'),
]

for claim, cat in claims:
    res = requests.post('http://127.0.0.1:8000/api/check-text', json={'text': claim}, timeout=30)
    data = res.json()
    ev = data.get('evidence', [])
    print(f'CLAIM: {claim}')
    print(f'VERDICT: {data.get("verdict")} | EVS: {len(ev)}')
    for e in ev[:3]:
        print(f'  [{e.get("relationship")}] {e.get("publisher")} - {e.get("title", "")[:60]}')
        print(f'    snippet: {e.get("evidence_excerpt","")[:100]}')
    print()
