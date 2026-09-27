from fastapi import APIRouter, HTTPException, Query
import logging
import feedparser
from datetime import datetime, timedelta
from typing import List, Optional
import time

from app.schemas.news import NewsResponse, NewsArticle

router = APIRouter(prefix="/news", tags=["News Feed"])
logger = logging.getLogger(__name__)

# Simple in-memory cache
_NEWS_CACHE = {
    "data": None,
    "timestamp": 0
}
CACHE_TTL_SECONDS = 300  # 5 minutes

# Real news sources
RSS_SOURCES = [
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "NASA", "url": "https://www.nasa.gov/news-release/feed/"},
    {"name": "UN News", "url": "https://news.un.org/feed/subscribe/en/news/all/rss.xml"}
]

def fetch_and_normalize_news() -> List[NewsArticle]:
    articles = []
    seen_urls = set()
    seen_titles = set()

    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            if not feed.entries:
                continue
            
            for entry in feed.entries[:10]: # limit per source
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                description = entry.get("summary", "")
                
                # Basic cleaning
                if not title or not link:
                    continue
                
                # Duplicate checking
                normalized_title = title.lower()
                if link in seen_urls or normalized_title in seen_titles:
                    continue
                    
                seen_urls.add(link)
                seen_titles.add(normalized_title)
                
                # Extract date if possible
                pub_date_str = ""
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    dt = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    pub_date_str = dt.isoformat() + "Z"
                elif hasattr(entry, "published"):
                    pub_date_str = entry.published
                else:
                    pub_date_str = datetime.utcnow().isoformat() + "Z"

                articles.append(NewsArticle(
                    title=title,
                    description=description[:250] + "..." if len(description) > 250 else description,
                    url=link,
                    source_name=source["name"],
                    published_at=pub_date_str,
                    image_url=None, # Extracting image from RSS reliably is complex; skip for simplicity
                    category="General"
                ))
        except Exception as e:
            logger.error(f"Error fetching RSS feed {source['name']}: {e}")
            
    # Sort by published_at descending (assuming ISO strings or best effort)
    articles.sort(key=lambda x: x.published_at, reverse=True)
    return articles

@router.get("", response_model=NewsResponse)
async def get_news(
    limit: int = Query(20, ge=1, le=50),
    force_refresh: bool = Query(False)
):
    global _NEWS_CACHE
    current_time = time.time()
    
    # Use cache if valid and refresh not forced
    if not force_refresh and _NEWS_CACHE["data"] is not None:
        if current_time - _NEWS_CACHE["timestamp"] < CACHE_TTL_SECONDS:
            return NewsResponse(
                articles=_NEWS_CACHE["data"][:limit],
                updated_at=datetime.fromtimestamp(_NEWS_CACHE["timestamp"]).isoformat() + "Z",
                status="success"
            )
            
    try:
        articles = fetch_and_normalize_news()
        _NEWS_CACHE["data"] = articles
        _NEWS_CACHE["timestamp"] = current_time
        
        return NewsResponse(
            articles=articles[:limit],
            updated_at=datetime.fromtimestamp(current_time).isoformat() + "Z",
            status="success"
        )
    except Exception as e:
        logger.error(f"News fetch failed: {e}")
        # Fallback to cache if available
        if _NEWS_CACHE["data"] is not None:
            return NewsResponse(
                articles=_NEWS_CACHE["data"][:limit],
                updated_at=datetime.fromtimestamp(_NEWS_CACHE["timestamp"]).isoformat() + "Z",
                status="success (cached)"
            )
        raise HTTPException(status_code=500, detail="Failed to load news")
