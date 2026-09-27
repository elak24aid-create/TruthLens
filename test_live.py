import requests
import time
import json
import os

BASE_URL = "https://truthlens-l1vq.onrender.com/api"

print("--- 1. HEALTH ---")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=60)
    print("Status:", r.status_code)
    print("Body:", r.json())
except Exception as e:
    print("Health failed:", e)

print("\n--- 2. NEWS ---")
try:
    r = requests.get(f"{BASE_URL}/news", timeout=60)
    print("Status:", r.status_code)
    data = r.json()
    print("Articles count:", len(data.get("articles", [])))
    if data.get("articles"):
        print("First article:", data["articles"][0]["title"])
except Exception as e:
    print("News failed:", e)

print("\n--- 3. FACT-CHECK LOGIC REGRESSION (TEXT) ---")
test_claims = [
    {"text": "Obama is the president of India.", "expected": "Not Genuine"},
    {"text": "The Sun is a star.", "expected": "Genuine / Insufficient"},
    {"text": "Covid-19 is caused by 5G cell towers.", "expected": "False / Misleading"}
]

for claim in test_claims:
    print(f"\nTesting Claim: {claim['text']}")
    try:
        t0 = time.time()
        r = requests.post(f"{BASE_URL}/check-text", json={"text": claim["text"]}, timeout=60)
        t1 = time.time()
        print(f"Status: {r.status_code} ({t1-t0:.2f}s)")
        if r.status_code == 200:
            data = r.json()
            print("Verdict:", data.get("verdict"))
            print("Summary:", data.get("summary"))
        else:
            print("Body:", r.text)
    except Exception as e:
        print("Check Text failed:", e)

print("\n--- 4. URL ---")
try:
    r = requests.post(f"{BASE_URL}/check-url", json={"url": "https://en.wikipedia.org/wiki/Earth"}, timeout=60)
    print("Status:", r.status_code)
    print("Verdict:", r.json().get("verdict"))
except Exception as e:
    print("URL check failed:", e)

print("\n--- 5. IMAGE OCR ---")
try:
    with open("test_ocr.jpg", "rb") as f:
        r = requests.post(f"{BASE_URL}/check-image", files={"file": f}, timeout=60)
    print("Status:", r.status_code)
    data = r.json()
    print("Verdict:", data.get("verdict"))
    print("Extracted Text:", data.get("extracted_metadata", {}).get("ocr_text"))
    print("OCR Status:", data.get("extracted_metadata", {}).get("ocr_status"))
except Exception as e:
    print("Image check failed:", e)
