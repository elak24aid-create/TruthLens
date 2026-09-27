import requests
import json
import time
from collections import defaultdict

# The local API url assuming I'll run the fastapi server
API_URL = "http://127.0.0.1:8000/api/check-text"

CLAIMS = [
    {"text": "The Sun is a star.", "expected": "LIKELY_GENUINE"},
    {"text": "Humans have landed on Mars.", "expected": "LIKELY_FALSE"},
    {"text": "The Earth orbits the Sun.", "expected": "LIKELY_GENUINE"},
    {"text": "The Eiffel Tower is in Paris.", "expected": "LIKELY_GENUINE"},
    {"text": "The Great Wall of China can be seen from the Moon with the naked eye.", "expected": "LIKELY_FALSE"}, # Often misleading/false
    {"text": "Water freezes at 0 degrees Celsius at standard atmospheric pressure.", "expected": "LIKELY_GENUINE"},
    {"text": "Obama is the president of India.", "expected": "LIKELY_FALSE"}, # Conflicting or false
    {"text": "Abraham Lincoln was the 16th US President.", "expected": "LIKELY_GENUINE"},
    {"text": "Covid-19 is caused by 5G cell towers.", "expected": "LIKELY_FALSE"}, # False
    {"text": "The Earth is flat.", "expected": "LIKELY_FALSE"}, # False
    {"text": "Albert Einstein invented the atomic bomb.", "expected": "LIKELY_FALSE"}, # Misleading/False
    {"text": "George Washington had wooden teeth.", "expected": "LIKELY_FALSE"}, # Misleading/False
    {"text": "Lightning never strikes the same place twice.", "expected": "LIKELY_FALSE"}, # Myth
    {"text": "Bats are blind.", "expected": "LIKELY_FALSE"}, # Myth
    {"text": "Mount Everest is the tallest mountain above sea level.", "expected": "LIKELY_GENUINE"},
    {"text": "Neil Armstrong was the first man to walk on the moon.", "expected": "LIKELY_GENUINE"},
    {"text": "Bulls are enraged by the color red.", "expected": "LIKELY_FALSE"}, # Myth
    {"text": "Goldfish have a three-second memory.", "expected": "LIKELY_FALSE"}, # Myth
    {"text": "Napoleon Bonaparte was extremely short.", "expected": "LIKELY_FALSE"}, # Myth
    {"text": "Diamonds are made from highly compressed coal.", "expected": "LIKELY_FALSE"} # Myth
]

results = []
matrix = defaultdict(int)

for claim in CLAIMS:
    try:
        start_time = time.time()
        response = requests.post(API_URL, json={"text": claim["text"]})
        elapsed = time.time() - start_time
        data = response.json()
        
        # Check verdict mapping
        # Let's consider LIKELY_FALSE and LIKELY_MISLEADING as FALSE for our eval, if expected is LIKELY_FALSE
        verdict = data.get("verdict")
        actual_is_false = verdict in ["LIKELY_FALSE", "LIKELY_MISLEADING"]
        actual_is_true = verdict == "LIKELY_GENUINE"
        actual_is_insufficient = verdict in ["INSUFFICIENT_EVIDENCE", "UNVERIFIED"]
        
        expected_is_false = claim["expected"] == "LIKELY_FALSE"
        expected_is_true = claim["expected"] == "LIKELY_GENUINE"
        
        if actual_is_false and expected_is_false:
            matrix["True Negative (Correctly False)"] += 1
            res_str = "CORRECT (False)"
        elif actual_is_true and expected_is_true:
            matrix["True Positive (Correctly True)"] += 1
            res_str = "CORRECT (True)"
        elif actual_is_insufficient:
            matrix["Insufficient Evidence"] += 1
            res_str = "INSUFFICIENT"
        elif actual_is_true and expected_is_false:
            matrix["False Positive (Falsely True)"] += 1
            res_str = "FALSE POSITIVE"
        elif actual_is_false and expected_is_true:
            matrix["False Negative (Falsely False)"] += 1
            res_str = "FALSE NEGATIVE"
        else:
            matrix["Other"] += 1
            res_str = "OTHER"

        print(f"[{res_str}] ({elapsed:.2f}s) Claim: '{claim['text']}' -> {verdict}")
        results.append({
            "claim": claim["text"],
            "expected": claim["expected"],
            "actual": verdict,
            "status": res_str,
            "time": elapsed
        })
    except Exception as e:
        print(f"Error checking {claim['text']}: {e}")

print("\n--- RESULTS ---")
for k, v in matrix.items():
    print(f"{k}: {v}")

total = len(CLAIMS)
correct = matrix["True Positive (Correctly True)"] + matrix["True Negative (Correctly False)"]
acc = correct / total * 100
print(f"Accuracy: {acc:.2f}% (excluding insufficient: {correct/(total - matrix['Insufficient Evidence'])*100 if (total - matrix['Insufficient Evidence']) > 0 else 0:.2f}%)")

