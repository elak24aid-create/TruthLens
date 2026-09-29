import requests
url = "http://127.0.0.1:8000/api"
res = requests.post(url + "/check-url", json={"url": "https://en.wikipedia.org/wiki/Earth"}).json()
print(res.get("verdict", res))
print("WHY:", res.get("why_this_verdict", res))
for ev in res.get("evidence", []): print(ev["source_type"], ev["domain"], ev["relationship"])
