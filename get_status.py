import requests
import json
import time

url = "https://truthlens-l1vq.onrender.com/api"

print("3. /health:", requests.get(url + "/health").status_code)

def check_text(t):
    return requests.post(url + "/check-text", json={"text": t + " " + str(time.time())}).json()

print("4. Sun:", check_text("The Sun is a star.")["verdict"])
print("5. Earth:", check_text("The Earth is flat.")["verdict"])
print("6. MJ:", check_text("Michael Jackson is the president of the United States.")["verdict"])

try:
    url_res = requests.post(url + "/check-url", json={"url": "https://en.wikipedia.org/wiki/Earth"}).json()
    print("7. URL:", url_res.get("status") or url_res.get("verdict"))
except Exception as e:
    print("7. URL:", str(e))

news = requests.get(url + "/news").json()
print("8. News Count:", len(news.get("articles", [])))
if len(news.get("articles", [])) > 0:
    print("9. Latest News:", news.get("articles", [{}])[0].get("published_at"))
else:
    print("9. Latest News: None")
