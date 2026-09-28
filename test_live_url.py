import requests
import json

URL = "https://truthlens-l1vq.onrender.com/api"

def test_url():
    target = "https://en.wikipedia.org/wiki/Earth"
    print(f"Checking URL: {target}")
    try:
        res = requests.post(f"{URL}/check-url", json={"url": target}, timeout=60)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Verdict: {data.get('verdict')}")
            print(f"Title: {data.get('extracted_metadata', {}).get('page_title')}")
            print(f"Publisher: {data.get('extracted_metadata', {}).get('publisher')}")
            print(f"Evidence Total: {len(data.get('evidence', []))}")
        else:
            print(res.text)
    except Exception as e:
        print(e)
        
test_url()
