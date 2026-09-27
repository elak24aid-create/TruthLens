import requests
import time
import json
import uuid

BASE_URL = "https://truthlens-l1vq.onrender.com/api"
session = requests.Session()

def print_section(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

# 1. HEALTH
print_section("1. HEALTH")
t0 = time.time()
r = session.get(f"{BASE_URL}/health", timeout=30)
t1 = time.time()
print(f"Status: {r.status_code} ({t1-t0:.2f}s)")
print("Body:", r.json())

# 2. IMAGE OCR
print_section("2. IMAGE OCR")
try:
    t0 = time.time()
    with open("test_ocr.jpg", "rb") as f:
        r = session.post(f"{BASE_URL}/check-image", files={"file": ("test_ocr.jpg", f, "image/jpeg")}, timeout=60)
    t1 = time.time()
    print(f"Status: {r.status_code} ({t1-t0:.2f}s)")
    if r.status_code == 200:
        data = r.json()
        print("Verdict:", data.get("verdict"))
        print("Extracted Text:", data.get("extracted_metadata", {}).get("ocr_text"))
        print("OCR Status:", data.get("extracted_metadata", {}).get("ocr_status"))
    else:
        print("Body:", r.text)
except Exception as e:
    print("Error:", e)

# 3. VIDEO OCR
print_section("3. VIDEO OCR")
try:
    t0 = time.time()
    with open("test_video.mp4", "rb") as f:
        r = session.post(f"{BASE_URL}/check-video", files={"file": ("test_video.mp4", f, "video/mp4")}, timeout=60)
    t1 = time.time()
    print(f"Status: {r.status_code} ({t1-t0:.2f}s)")
    if r.status_code == 200:
        data = r.json()
        print("Verdict:", data.get("verdict"))
        print("Extracted Text:", data.get("extracted_metadata", {}).get("ocr_text"))
        print("OCR Status:", data.get("extracted_metadata", {}).get("ocr_status"))
    else:
        print("Body:", r.text)
except Exception as e:
    print("Error:", e)

# 4. TEXT FACT-CHECK
print_section("4. TEXT FACT-CHECK")
claims = [
    "Obama is the president of India",
    "The Sun is a star.",
    "Humans have landed on Mars."
]
for claim in claims:
    t0 = time.time()
    r = session.post(f"{BASE_URL}/check-text", json={"text": claim}, timeout=60)
    t1 = time.time()
    print(f"\nClaim: {claim}")
    print(f"Status: {r.status_code} ({t1-t0:.2f}s)")
    if r.status_code == 200:
        d = r.json()
        print("Verdict:", d.get("verdict"))
        print("Confidence:", d.get("confidence"))
        print("Evidence Count:", len(d.get("evidence", [])))
    else:
        print("Body:", r.text)

# 5. URL CHECK
print_section("5. URL CHECK")
t0 = time.time()
r = session.post(f"{BASE_URL}/check-url", json={"url": "https://en.wikipedia.org/wiki/Earth"}, timeout=60)
t1 = time.time()
print(f"Status: {r.status_code} ({t1-t0:.2f}s)")
if r.status_code == 200:
    d = r.json()
    print("Verdict:", d.get("verdict"))
    print("Evidence Count:", len(d.get("evidence", [])))
    print("Claims Found:", d.get("extracted_metadata", {}).get("claims_found"))
else:
    print("Body:", r.text)

# 6. NEWS
print_section("6. NEWS")
t0 = time.time()
r = session.get(f"{BASE_URL}/news", timeout=60)
t1 = time.time()
print(f"Status: {r.status_code} ({t1-t0:.2f}s)")
if r.status_code == 200:
    d = r.json()
    arts = d.get("articles", [])
    print(f"Articles: {len(arts)}")
    if arts:
        print(f"First Article: {arts[0]['title']} | URL: {arts[0]['url']} | Published: {arts[0]['published_at']}")
else:
    print("Body:", r.text)

# 7. AUTH / HISTORY / REPORTS
print_section("7. AUTH / HISTORY / REPORTS")
email = f"test_{uuid.uuid4().hex[:8]}@example.com"
pw = "Testpass123!"

# Register
r = session.post(f"{BASE_URL}/auth/register", json={"email": email, "password": pw, "full_name": "Test User"}, timeout=30)
print(f"Register Status: {r.status_code}")

# Login
r = session.post(f"{BASE_URL}/auth/login", json={"email": email, "password": pw}, timeout=30)
print(f"Login Status: {r.status_code}")
token = None
if r.status_code == 200:
    token = r.json().get("token")

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # History
    r = session.get(f"{BASE_URL}/history", headers=headers, timeout=30)
    print(f"History Status: {r.status_code}")
    
    # Reports
    r = session.get(f"{BASE_URL}/report", headers=headers, timeout=30)
    print(f"Reports Status: {r.status_code}")
