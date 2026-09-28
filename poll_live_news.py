import requests, time, json

URL = "https://truthlens-l1vq.onrender.com/api"
print("Waiting for Render to deploy new news endpoint...", flush=True)

start_time = time.time()
while True:
    try:
        res = requests.get(f"{URL}/news?category=World&limit=2", timeout=30)
        if res.status_code == 200:
            data = res.json()
            articles = data.get("articles", [])
            if len(articles) > 0 and 'category' in articles[0]:
                print(f"\nDeploy is live! Found {len(articles)} articles.", flush=True)
                print(json.dumps(articles[0], indent=2))
                break
            else:
                elapsed = int(time.time() - start_time)
                print(f"[{elapsed}s] Still old code. Retrying in 15s...", flush=True)
        else:
            print(f"Error {res.status_code}. Retrying in 15s...", flush=True)
    except Exception as e:
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s] Failed: {e}. Retrying in 15s...", flush=True)
    time.sleep(15)
    
    if time.time() - start_time > 900: # 15 minutes timeout
        print("Timeout reached.", flush=True)
        break
