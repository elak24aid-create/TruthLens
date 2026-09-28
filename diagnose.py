import requests
import time
import json

URL = "https://truthlens-l1vq.onrender.com/api"

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
        else:
            print(f"Error: {res.status_code} {res.text}")
    except Exception as e:
        print(f"Failed: {e}")

def check_url(url):
    print(f"\n--- Checking URL: {url} ---")
    start = time.time()
    try:
        res = requests.post(f"{URL}/check-url", json={"url": url})
        end = time.time()
        print(f"Time: {end - start:.2f}s")
        if res.status_code == 200:
            data = res.json()
            print(f"Verdict: {data.get('verdict')}")
            print(f"Extracted Title: {data.get('extracted_metadata', {}).get('title')}")
        else:
            print(f"Error: {res.status_code} {res.text}")
    except Exception as e:
        print(f"Failed: {e}")

def check_news():
    print(f"\n--- Checking News ---")
    start = time.time()
    try:
        res = requests.get(f"{URL}/news?force_refresh=true")
        end = time.time()
        print(f"Time: {end - start:.2f}s")
        if res.status_code == 200:
            data = res.json()
            arts = data.get('articles', [])
            print(f"Articles: {len(arts)}")
            if arts:
                print(f"Newest: {arts[0].get('published_at')}")
                print(f"Oldest: {arts[-1].get('published_at')}")
        else:
            print(f"Error: {res.status_code} {res.text}")
    except Exception as e:
        print(f"Failed: {e}")

claims = [
    "The Sun is a star.",
    "Michael Jackson is the president of the United States.",
    "Michael Jackson's manager had cancer.",
    "Humans have landed on Mars."
]

for c in claims:
    check_text(c)

check_url("https://en.wikipedia.org/wiki/Earth")
check_news()

def check_image():
    print('\n--- Checking Image ---')
    try:
        with open('test_image.png', 'rb') as f:
            resp = requests.post(f'{URL}/check-image', files={'file': f})
            data = resp.json()
            ocr_text = data.get('extracted_metadata', {}).get('ocr_text', '')
            print(f'Status: {resp.status_code}')
            print(f'OCR Text: {ocr_text}')
    except Exception as e:
        print(f'Error: {e}')

check_image()

def check_video():
    print('\n--- Checking Video ---')
    try:
        with open('test_video.mp4', 'rb') as f:
            resp = requests.post(f'{URL}/check-video', files={'file': ('test_video.mp4', f, 'video/mp4')})
            data = resp.json()
            ocr_text = data.get('extracted_metadata', {}).get('ocr_text', '')
            print(f'Status: {resp.status_code}')
            print(f'OCR Text: {ocr_text}')
    except Exception as e:
        print(f'Error: {e}')

check_video()

def check_health():
    print('\n--- Checking Health ---')
    try:
        resp = requests.get(f'{URL}/health')
        print(f'Status: {resp.status_code}')
    except Exception as e:
        print(f'Error: {e}')

check_health()

def check_image2():
    print('\n--- Checking Image Retry ---')
    try:
        with open('test_image.png', 'rb') as f:
            resp = requests.post(f'{URL}/check-image', files={'file': ('test_image.png', f, 'image/png')})
            data = resp.json()
            ocr_text = data.get('extracted_metadata', {}).get('ocr_text', '')
            print(f'Status: {resp.status_code}')
            print(f'OCR Text: {ocr_text}')
    except Exception as e:
        print(f'Error: {e}')

check_image2()
