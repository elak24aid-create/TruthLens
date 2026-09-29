import requests
import time

base_url = "https://truthlens-l1vq.onrender.com/api"

print("--- GET /health ---")
r = requests.get(f"{base_url}/health")
print("Status:", r.status_code)
print()

claims = [
    "The Sun is a star.  ",
    "The Earth is flat.  ",
    "Michael Jackson is the president of the United States.  ",
    "2 + 2 = 5.  "
]

for c in claims:
    print(f"--- Text: {c} ---")
    start = time.time()
    try:
        r = requests.post(f"{base_url}/check-text", json={"text": c, "language": "English"}, timeout=60)
        res = r.json()
        end = time.time()
        print("Status:", r.status_code)
        print("Time:", round(end - start, 2), "s")
        print("Verdict:", res.get("verdict"))
        print("Evidence Count:", len(res.get("evidence", [])))
        
        sources = set()
        for ev in res.get("evidence", []):
            sources.add(ev.get("publisher", "Unknown"))
        print("Sources Used:", ", ".join(sources))
        
    except Exception as e:
        print("Error:", e)
    print()

print("--- URL: https://en.wikipedia.org/wiki/Earth ---")
start = time.time()
try:
    r = requests.post(f"{base_url}/check-url", json={"url": "https://en.wikipedia.org/wiki/Earth", "language": "English"}, timeout=60)
    res = r.json()
    end = time.time()
    print("Status:", r.status_code)
    print("Time:", round(end - start, 2), "s")
    print("Verdict:", res.get("verdict"))
    print("Evidence Count:", len(res.get("evidence", [])))
except Exception as e:
    print("Error:", e)
print()

print("--- /news ---")
start = time.time()
try:
    r = requests.get(f"{base_url}/news", timeout=60)
    res = r.json()
    end = time.time()
    print("Status:", r.status_code)
    print("Time:", round(end - start, 2), "s")
    articles = res.get("articles", [])
    print("News Count:", len(articles))
except Exception as e:
    print("Error:", e)
print()
