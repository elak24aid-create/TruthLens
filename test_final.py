import requests
import time

claims = [
    "The Sun is a star.",
    "The Earth is flat.",
    "Michael Jackson is the president of the United States.",
    "Water freezes at 0 degrees Celsius at standard atmospheric pressure.",
    "2 + 2 = 5.",
    "The Earth orbits the Sun.",
    "Paris is the capital of France.",
    "Michael Jackson's manager had cancer."
]

url = 'https://truthlens-l1vq.onrender.com/api/check-text'

for c in claims:
    print(f"\n--- Checking: {c} ---")
    try:
        r = requests.post(url, json={'text': c, 'language': 'English'}, timeout=60)
        res = r.json()
        print(f"VERDICT: {res.get('verdict')} | CONF: {res.get('confidence')}")
        print(f"MODE: {res.get('verification_mode')}")
    except Exception as e:
        print("Failed:", e)
    time.sleep(2)
