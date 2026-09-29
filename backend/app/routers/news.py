from fastapi import APIRouter, HTTPException, Query
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import time
import requests
from ddgs import DDGS
import feedparser
from urllib.parse import quote
from email.utils import parsedate_to_datetime
import re

from app.schemas.news import NewsResponse, NewsArticle

router = APIRouter(prefix="/news", tags=["News Feed"])
logger = logging.getLogger(__name__)

# Simple in-memory cache keyed by (category, query)
_NEWS_CACHE = {}
CACHE_TTL_SECONDS = 240  # 4 minutes

def fetch_rss(query: str, category: str, limit: int) -> List[NewsArticle]:
    articles = []
    try:
        url = ""
        if query and query.strip():
            url = f"https://news.google.com/rss/search?q={quote(query.strip())}&hl=en-US&gl=US&ceid=US:en"
        elif category and category.lower() != "all":
            # Map category to Google News topic
            cat_map = {
                "world": "WORLD",
                "technology": "TECHNOLOGY",
                "science": "SCIENCE",
                "sports": "SPORTS",
                "business": "BUSINESS",
                "health": "HEALTH",
                "india": "NATION" # Assuming Nation for India if localized, but we use US/en. Let's just search it.
            }
            if category.lower() == "india":
                url = "https://news.google.com/rss/search?q=India&hl=en-IN&gl=IN&ceid=IN:en"
            else:
                topic = cat_map.get(category.lower(), "WORLD")
                url = f"https://news.google.com/rss/headlines/section/topic/{topic}?hl=en-US&gl=US&ceid=US:en"
        else:
            url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"

        import urllib.request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        xml = urllib.request.urlopen(req, timeout=10).read()
        feed = feedparser.parse(xml)
        
        for entry in feed.entries[:limit]:
            try:
                dt = parsedate_to_datetime(entry.published)
                dt_iso = dt.isoformat() + "Z"
            except:
                dt_iso = datetime.utcnow().isoformat() + "Z"
                
            source = entry.source.title if hasattr(entry, 'source') else "Google News"
            title = entry.title
            if not title or not entry.link:
                continue
            if " - " in title:
                title = title.rsplit(" - ", 1)[0]
                
            image_url = None
            if hasattr(entry, 'media_content') and len(entry.media_content) > 0:
                image_url = entry.media_content[0].get('url')
            
            articles.append(NewsArticle(
                title=title,
                description=title, 
                url=entry.link,
                source_name=source,
                published_at=dt_iso,
                image_url=image_url,
                category=category or "All"
            ))
    except Exception as e:
        logger.warning(f"RSS fetch failed: {e}")
    return articles

def parse_ddgs_date(date_str: str) -> str:
    if not date_str:
        return datetime.utcnow().isoformat() + "Z"
    if "h" in date_str.lower() and "t" not in date_str.lower():
        try:
            h = int(re.search(r'\d+', date_str).group())
            return (datetime.utcnow() - timedelta(hours=h)).isoformat() + "Z"
        except:
            pass
    elif "d" in date_str.lower() and "t" not in date_str.lower():
        try:
            d = int(re.search(r'\d+', date_str).group())
            return (datetime.utcnow() - timedelta(days=d)).isoformat() + "Z"
        except:
            pass
    elif "m" in date_str.lower() and "t" not in date_str.lower():
        try:
            m = int(re.search(r'\d+', date_str).group())
            return (datetime.utcnow() - timedelta(minutes=m)).isoformat() + "Z"
        except:
            pass
    return date_str

def fetch_ddgs(query: str, limit: int) -> List[NewsArticle]:
    articles = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=limit))
            for res in results:
                title = res.get("title", "").strip()
                url = res.get("url", "")
                if not title or not url:
                    continue
                articles.append(NewsArticle(
                    title=title,
                    description=res.get("body", ""),
                    url=url,
                    source_name=res.get("source", "News Source"),
                    published_at=parse_ddgs_date(res.get("date", "")),
                    image_url=res.get("image", None),
                    category=query
                ))
    except Exception as e:
        logger.warning(f"DDGS fetch failed: {e}")
    return articles

def deduplicate_articles(articles: List[NewsArticle]) -> List[NewsArticle]:
    seen_urls = set()
    seen_titles = set()
    unique = []
    for a in articles:
        normalized_title = a.title.lower()
        if a.url in seen_urls or normalized_title in seen_titles:
            continue
        seen_urls.add(a.url)
        seen_titles.add(normalized_title)
        unique.append(a)
    return unique

@router.get("", response_model=NewsResponse)
async def get_news(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query("All", description="News category"),
    limit: int = Query(20, ge=1, le=50),
    force_refresh: bool = Query(False)
):
    global _NEWS_CACHE
    current_time = time.time()
    
    cache_key = f"{str(query).lower()}_{str(category).lower()}"
    
    # If not forcing refresh, check cache
    if not force_refresh and cache_key in _NEWS_CACHE:
        cached_data = _NEWS_CACHE[cache_key]
        if current_time - cached_data["timestamp"] < CACHE_TTL_SECONDS:
            return NewsResponse(
                articles=cached_data["data"][:limit],
                updated_at=datetime.fromtimestamp(cached_data["timestamp"]).isoformat() + "Z",
                status="success"
            )
            
    # Determine actual search term
    search_term = ""
    if query and query.strip():
        search_term = query.strip()
    elif category and category.lower() != "all":
        search_term = category.strip()
    else:
        search_term = "world news" # default generic fallback

    try:
        # Try RSS First
        articles = fetch_rss(query, category, limit=limit*2)
        
        # Fallback to DDGS if RSS returned nothing
        if not articles:
            articles = fetch_ddgs(search_term, limit=limit*2)
            
        articles = deduplicate_articles(articles)
        
        # Sort by actual published_at descending
        articles.sort(key=lambda x: x.published_at, reverse=True)
        
        # If still empty but we have an old cache, return it instead of empty
        if not articles and cache_key in _NEWS_CACHE:
            cached_data = _NEWS_CACHE[cache_key]
            return NewsResponse(
                articles=cached_data["data"][:limit],
                updated_at=datetime.fromtimestamp(cached_data["timestamp"]).isoformat() + "Z",
                status="success (cached fallback)"
            )
            
        if not articles:
            return NewsResponse(
                articles=[],
                updated_at=datetime.fromtimestamp(current_time).isoformat() + "Z",
                status="success"
            )

        _NEWS_CACHE[cache_key] = {
            "data": articles,
            "timestamp": current_time
        }
        
        return NewsResponse(
            articles=articles[:limit],
            updated_at=datetime.fromtimestamp(current_time).isoformat() + "Z",
            status="success"
        )
    except Exception as e:
        logger.error(f"News fetch completely failed: {e}")
        if cache_key in _NEWS_CACHE:
            cached_data = _NEWS_CACHE[cache_key]
            return NewsResponse(
                articles=cached_data["data"][:limit],
                updated_at=datetime.fromtimestamp(cached_data["timestamp"]).isoformat() + "Z",
                status="success (cached)"
            )
        raise HTTPException(status_code=500, detail="Failed to load news")
