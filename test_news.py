import requests
from datetime import datetime

url = "https://truthlens-l1vq.onrender.com/api/news"
try:
    news = requests.get(url).json()

    print("NEWS_COUNT:", len(news.get("articles", [])))
    if len(news.get("articles", [])) >= 2:
        print("NEWEST_ARTICLE:", news["articles"][0].get("published_at"))
        print("SECOND_NEWEST_ARTICLE:", news["articles"][1].get("published_at"))
        
        dt1 = datetime.fromisoformat(news["articles"][0].get("published_at").replace('Z', '+00:00'))
        dt2 = datetime.fromisoformat(news["articles"][1].get("published_at").replace('Z', '+00:00'))
        print("NEWS_SORTING:", "PASS" if dt1 >= dt2 else "FAIL")
    else:
        print("NEWEST_ARTICLE: NONE")
        print("SECOND_NEWEST_ARTICLE: NONE")
        print("NEWS_SORTING: FAIL")

    print("SERVER_TIME:", news.get("updated_at"))
except Exception as e:
    print("ERROR:", str(e))
