import requests
import time
import json
from datetime import datetime

base_url = "https://truthlens-l1vq.onrender.com/api"

# Health
r = requests.get(f"{base_url}/health")
print("HEALTH:", r.status_code)

# Text
start = time.time()
r = requests.post(f"{base_url}/check-text", json={"text": "The Sun is a star.", "language": "English"}, timeout=60)
end = time.time()
print("TEXT TIME:", round(end - start, 2))
print("TEXT RESULT:", r.json().get('verdict'))

# URL
start = time.time()
r = requests.post(f"{base_url}/check-url", json={"url": "https://en.wikipedia.org/wiki/Earth", "language": "English"}, timeout=60)
end = time.time()
print("URL TIME:", round(end - start, 2))
print("URL RESULT:", r.json().get('verdict'))

# News
start = time.time()
r = requests.get(f"{base_url}/news", timeout=60)
end = time.time()
print("NEWS TIME:", round(end - start, 2))
articles = r.json().get('articles', [])
print("NEWS COUNT:", len(articles))
if len(articles) > 0:
    print("LAST TIMESTAMP:", articles[0].get('published_at'))
print("LAST CHECKED TIMESTAMP:", r.json().get('updated_at'))
