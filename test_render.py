import requests
import time

url = "https://truthlens-l1vq.onrender.com/api"

try:
    print("3. Render /api/health status:", requests.get(url + "/health").status_code)
except Exception as e:
    print("3. Render /api/health status:", str(e))

def check_text(t):
    try:
        return requests.post(url + "/check-text", json={"text": t + " " + str(time.time())}).json().get("verdict", "ERROR")
    except Exception as e:
        return str(e)

print("4. Live Render result for 'The Sun is a star.':", check_text("The Sun is a star."))
print("5. Live Render result for 'The Earth is flat.':", check_text("The Earth is flat."))
print("6. Live Render result for 'Michael Jackson is the president of the United States.':", check_text("Michael Jackson is the president of the United States."))

try:
    res = requests.post(url + "/check-url", json={"url": "https://en.wikipedia.org/wiki/Earth"}).json()
    print("7. Live Render URL test for https://en.wikipedia.org/wiki/Earth:", res.get("verdict", res.get("detail", "UNKNOWN")))
except Exception as e:
    print("7. Live Render URL test for https://en.wikipedia.org/wiki/Earth:", str(e))

try:
    news = requests.get(url + "/news").json()
    print("8. Live Render /news article count:", len(news.get("articles", [])))
    if news.get("articles"):
        print("9. Latest news article published_at:", news["articles"][0].get("published_at"))
    else:
        print("9. Latest news article published_at: NONE")
except Exception as e:
    print("8. Live Render /news article count: ERROR")
    print("9. Latest news article published_at: ERROR")
