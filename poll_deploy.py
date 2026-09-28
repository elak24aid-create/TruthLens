import requests
import time

while True:
    try:
        r = requests.post("https://truthlens-l1vq.onrender.com/api/check-text", json={"text": "2 + 2 = 5.", "language": "English"}, timeout=60)
        res = r.json()
        print(f"VERDICT: {res.get('verdict')}")
        if res.get('verdict') == 'Likely Misleading':
            print("DEPLOYMENT IS LIVE AND CORRECT!")
            break
        print("Still returning old behavior...")
    except Exception as e:
        print("Error or timeout, deployment might be restarting...", e)
    time.sleep(10)
