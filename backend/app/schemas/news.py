from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class NewsArticle(BaseModel):
    title: str
    description: str
    url: str
    source_name: str
    published_at: str
    image_url: Optional[str] = None
    category: Optional[str] = None

class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    updated_at: str
    status: str
