from ddgs import DDGS
import json

def test_ddgs():
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news("India", max_results=5))
            print(json.dumps(results, indent=2))
    except Exception as e:
        print(e)
        
test_ddgs()
