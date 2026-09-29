import requests
url = "http://127.0.0.1:8000/api"
res = requests.post(url + "/check-text", json={"text": "Water freezes at 0 degrees Celsius at standard atmospheric pressure."}).json()
print(res.get("verdict", res))
for ev in res.get("evidence", []): print(ev["source_type"], ev["domain"], ev["relationship"])
