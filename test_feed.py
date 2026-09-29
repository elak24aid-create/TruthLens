import feedparser
from urllib.parse import quote
from datetime import datetime
from email.utils import parsedate_to_datetime

def fetch_rss(query: str, limit: int):
    # Google News RSS
    url = f"https://news.google.com/rss/search?q={quote(query)}"
    feed = feedparser.parse(url)
    for entry in feed.entries[:3]:
        try:
            dt = parsedate_to_datetime(entry.published)
            dt_iso = dt.isoformat() + "Z"
        except:
            dt_iso = datetime.utcnow().isoformat() + "Z"
            
        source = entry.source.title if 'source' in entry else "Google News"
        title = entry.title
        # Sometimes source is appended to title "Title - Source"
        if " - " in title:
            title = title.rsplit(" - ", 1)[0]
            
        print("Title:", title)
        print("Date:", dt_iso)
        print("Source:", source)
        print("URL:", entry.link)

fetch_rss("world news", 5)
