import requests
import json

def test_gdelt():
    try:
        url = "https://api.gdeltproject.org/api/v2/doc/doc?query=sourcecountry:IN&mode=artlist&maxrecords=5&format=json"
        res = requests.get(url, timeout=5)
        print(json.dumps(res.json(), indent=2))
    except Exception as e:
        print(e)
        
test_gdelt()
