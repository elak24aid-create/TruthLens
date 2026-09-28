from functools import lru_cache
import urllib.request
import urllib.parse
import ipaddress
import socket
from bs4 import BeautifulSoup
import json

def is_safe_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False
            
        hostname = parsed.hostname
        if not hostname:
            return False

        # Block explicit localhost / private IP literal strings
        if hostname.lower() in ["localhost", "127.0.0.1", "0.0.0.0", "::1"]:
            return False

        # Resolve IP to check for private ranges (SSRF protection)
        try:
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                return False
        except socket.gaierror:
            # Cannot resolve
            return False
            
        return True
    except Exception:
        return False

@lru_cache(maxsize=100)
def fetch_and_extract_article(url: str) -> dict:
    """
    Safely fetches the URL and extracts metadata + text.
    """
    if not is_safe_url(url):
        raise ValueError("Invalid or disallowed URL.")

    # Safe fetching with timeout and limits
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'TruthLens/1.0 (Research Bot)'}
    )
    
    try:
        # 10s timeout
        with urllib.request.urlopen(req, timeout=10) as response:
            # Check content type
            content_type = response.headers.get_content_type()
            if 'text/html' not in content_type and 'text/plain' not in content_type:
                raise ValueError(f"Unsupported content type: {content_type}")
                
            # Limit read size (e.g., 2MB)
            html = response.read(2 * 1024 * 1024)
    except Exception as e:
        raise ValueError(f"Failed to fetch URL: {str(e)}")

    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract metadata
    title = ""
    if soup.title:
        title = soup.title.string.strip()
        
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title.get("content").strip()

    description = ""
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        description = og_desc.get("content").strip()
    else:
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc.get("content").strip()

    source_name = ""
    og_site_name = soup.find("meta", property="og:site_name")
    if og_site_name and og_site_name.get("content"):
        source_name = og_site_name.get("content").strip()
    else:
        parsed_url = urllib.parse.urlparse(url)
        source_name = parsed_url.hostname

    published_at = ""
    article_published_time = soup.find("meta", property="article:published_time")
    if article_published_time and article_published_time.get("content"):
        published_at = article_published_time.get("content").strip()

    # Extract article text
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
        script.decompose()

    # Get text
    article_text = soup.get_text(separator=' ')
    
    # Clean up whitespace
    lines = (line.strip() for line in article_text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    article_text = ' '.join(chunk for chunk in chunks if chunk)

    # Limit article text to prevent overloading ML
    if len(article_text) > 20000:
        article_text = article_text[:20000] + "... [Article Truncated]"
        
    if not article_text.strip():
        raise ValueError("Could not extract any text from the article.")

    # Formulate claim text for searching
    claim_text = title
    if description and len(claim_text) < 60:
        claim_text += " - " + description
    
    # If title/desc are empty or very short, use the first chunk of text
    if len(claim_text) < 30:
        first_sentence = article_text.split('.')[0]
        claim_text += " - " + first_sentence[:100]

    if len(claim_text) > 150:
        claim_text = claim_text[:147] + "..."

    return {
        "title": title,
        "description": description,
        "source_name": source_name,
        "published_at": published_at,
        "article_text": article_text,
        "claim_text": claim_text,
    }
