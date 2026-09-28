import requests
import time
import json

URL = "http://127.0.0.1:8000/api"

def check_text(claim):
    print(f"\n--- Checking: {claim} ---")
    start = time.time()
    try:
        res = requests.post(f"{URL}/check-text", json={"text": claim, "context": "Android test"})
        end = time.time()
        print(f"Time: {end - start:.2f}s")
        if res.status_code == 200:
            data = res.json()
            print(f"Verdict: {data.get('verdict')}")
            print(f"Confidence: {data.get('confidence')}")
            ev = data.get('evidence', [])
            sup = sum(1 for e in ev if e.get('relationship') == 'supporting')
            con = sum(1 for e in ev if e.get('relationship') == 'conflicting')
            ctx = sum(1 for e in ev if e.get('relationship') == 'context')
            print(f"Evidence Total: {len(ev)} (Sup: {sup}, Con: {con}, Ctx: {ctx})")
            for e in ev:
                print(f" - [{e.get('relationship')}] {e.get('title')} ({e.get('source_type')})")
            print(f"Reason: {data.get('summary')}")
        else:
            print(f"Error: {res.status_code} {res.text}")
    except Exception as e:
        print(f"Failed: {e}")

claims = [
    "Michael Jackson is the president of the United States.",
    "The Sun is a star.",
    "The Earth is flat.",
    "2 + 2 = 5.",
    "Water freezes at 0 degrees Celsius at standard atmospheric pressure.",
    "Michael Jackson's manager had cancer."
]

for c in claims:
    check_text(c)
