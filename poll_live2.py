import requests, time, sys

URL = "https://truthlens-l1vq.onrender.com/api"
print("Waiting for Render to deploy new code (checking Michael Jackson contradiction)...", flush=True)

start_time = time.time()
while True:
    try:
        res = requests.post(f"{URL}/check-text", json={"text": "Michael Jackson is the president of the United States.", "context": ""}, timeout=30)
        if res.status_code == 200:
            data = res.json()
            verdict = data.get("verdict")
            if verdict == "Likely Misleading":
                print(f"\nDeploy is live! Verdict: {verdict}", flush=True)
                break
            else:
                elapsed = int(time.time() - start_time)
                print(f"[{elapsed}s] Still old code (Verdict: {verdict}). Retrying in 15s...", flush=True)
        else:
            print(f"Error {res.status_code}. Retrying in 15s...", flush=True)
    except Exception as e:
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s] Failed: {e}. Retrying in 15s...", flush=True)
    time.sleep(15)
    
    if time.time() - start_time > 900: # 15 minutes timeout
        print("Timeout reached.", flush=True)
        break
