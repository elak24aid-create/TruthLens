import requests, time, sys

URL = "https://truthlens-l1vq.onrender.com/api"
print("Waiting for Render to deploy new code (checking URL extraction)...", flush=True)

start_time = time.time()
while True:
    try:
        res = requests.post(f"{URL}/check-url", json={"url": "https://en.wikipedia.org/wiki/Earth"}, timeout=30)
        if res.status_code == 200:
            data = res.json()
            title = data.get("extracted_metadata", {}).get("title")
            if title and title != "None":
                print(f"\nDeploy is live! Extracted Title: {title}", flush=True)
                break
            else:
                elapsed = int(time.time() - start_time)
                print(f"[{elapsed}s] Still old code (metadata dropped). Retrying in 15s...", flush=True)
        else:
            print(f"Error {res.status_code}. Retrying in 15s...", flush=True)
    except Exception as e:
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s] Failed: {e}. Retrying in 15s...", flush=True)
    time.sleep(15)
    
    if time.time() - start_time > 900: # 15 minutes timeout
        print("Timeout reached.", flush=True)
        break
