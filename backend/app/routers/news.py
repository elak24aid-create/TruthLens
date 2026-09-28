from fastapi import APIRouter, HTTPException, Query
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import time
import requests
from ddgs import DDGS
from urllib.parse import quote

from app.schemas.news import NewsResponse, NewsArticle

router = APIRouter(prefix="/news", tags=["News Feed"])
logger = logging.getLogger(__name__)

# Simple in-memory cache keyed by (category, query)
_NEWS_CACHE = {}
CACHE_TTL_SECONDS = 240  # 4 minutes

def parse_gdelt_date(date_str: str) -> str:
    try:
        # GDELT format: 20260928T031500Z
        if len(date_str) == 16 and 'T' in date_str and date_str.endswith('Z'):
            dt = datetime.strptime(date_str, "%Y%m%dT%H%M%SZ")
            return dt.isoformat() + "Z"
    except Exception:
        pass
    return datetime.utcnow().isoformat() + "Z"

def fetch_gdelt(query: str, limit: int) -> List[NewsArticle]:
    articles = []
    try:
        # GDELT URL format
        encoded_query = quote(query)
        url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={encoded_query}&mode=artlist&maxrecords={limit}&format=json"
        res = requests.get(url, timeout=4) # fast timeout
        if res.status_code == 200:
            data = res.json()
            if "articles" in data:
                for item in data["articles"]:
                    title = item.get("title", "").strip()
                    url = item.get("url", "")
                    if not title or not url:
                        continue
                        
                    raw_date = item.get("seendate", "")
                    published_at = parse_gdelt_date(raw_date) if raw_date else datetime.utcnow().isoformat() + "Z"
                    
                    articles.append(NewsArticle(
                        title=title,
                        description=title, # GDELT artlist often doesn't give a good snippet
                        url=url,
                        source_name=item.get("domain", "GDELT Source"),
                        published_at=published_at,
                        image_url=item.get("socialimage", None),
                        category=query
                    ))
    except Exception as e:
        logger.warning(f"GDELT fetch failed: {e}")
    return articles

import re

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
        # Try GDELT First
        articles = fetch_gdelt(search_term, limit=limit*2)
        
        # Fallback to DDGS if GDELT returned nothing
        if not articles:
            articles = fetch_ddgs(search_term, limit=limit*2)
            
        articles = deduplicate_articles(articles)
        
        # Sort by published_at descending
        articles.sort(key=lambda x: x.published_at, reverse=True)
        
        if not articles:
            # Only return empty if both failed entirely
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
