import re
from urllib.parse import urlparse
from typing import Dict, Any, Optional

# Verified transparency & established international/regional news agencies
# Used as one signal only (never absolute proof)
ESTABLISHED_OUTLETS = {
    "reuters.com": {"name": "Reuters", "type": "International News Agency", "credibility_tier": "High Transparency"},
    "apnews.com": {"name": "Associated Press", "type": "News Agency", "credibility_tier": "High Transparency"},
    "bbc.com": {"name": "BBC News", "type": "Public Broadcaster", "credibility_tier": "High Transparency"},
    "bbc.co.uk": {"name": "BBC News", "type": "Public Broadcaster", "credibility_tier": "High Transparency"},
    "thehindu.com": {"name": "The Hindu", "type": "Major Newspaper", "credibility_tier": "High Transparency"},
    "indianexpress.com": {"name": "Indian Express", "type": "Major Newspaper", "credibility_tier": "High Transparency"},
    "ndtv.com": {"name": "NDTV", "type": "Broadcaster", "credibility_tier": "Moderate Transparency"},
    "pib.gov.in": {"name": "Press Information Bureau (Gov)", "type": "Official Government Source", "credibility_tier": "High Transparency"},
    "who.int": {"name": "World Health Organization", "type": "International Health Authority", "credibility_tier": "High Transparency"},
    "cdc.gov": {"name": "Centers for Disease Control", "type": "Health Authority", "credibility_tier": "High Transparency"},
    "theonion.com": {"name": "The Onion", "type": "Satirical Publication", "credibility_tier": "Satire"},
    "babylonbee.com": {"name": "Babylon Bee", "type": "Satirical Publication", "credibility_tier": "Satire"},
}


def extract_domain(url_or_text: str) -> Optional[str]:
    """
    Extracts canonical domain name from URL or embedded text references.
    """
    if not url_or_text:
        return None

    # If it's a URL
    if url_or_text.startswith("http://") or url_or_text.startswith("https://"):
        parsed = urlparse(url_or_text)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc

    # Extract URL pattern inside text
    url_match = re.search(r"https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", url_or_text)
    if url_match:
        return url_match.group(1).lower()

    return None


def analyze_source_credibility(url_or_text: str) -> Dict[str, Any]:
    """
    Evaluates source transparency signals without claiming 100% guarantee.
    """
    domain = extract_domain(url_or_text)
    is_https = url_or_text.lower().startswith("https://") if url_or_text.startswith("http") else None

    if not domain:
        return {
            "domain": None,
            "publisher": None,
            "status": "not_found",
            "is_https": is_https,
            "tier": "Source Unknown / Direct Text",
            "is_satire": False,
            "explanation": "No specific publisher URL or domain was identified in the submitted content.",
        }

    # Check known publishers
    matched = ESTABLISHED_OUTLETS.get(domain)
    if matched:
        is_satire = matched["type"] == "Satirical Publication"
        return {
            "domain": domain,
            "publisher": matched["name"],
            "status": "found",
            "is_https": is_https,
            "tier": matched["credibility_tier"],
            "is_satire": is_satire,
            "explanation": (
                f"Publisher identified as '{matched['name']}' ({matched['type']}). "
                "Historical publishing transparency is documented."
            ),
        }

    # Generic domain found but not in catalog
    return {
        "domain": domain,
        "publisher": domain,
        "status": "found",
        "is_https": is_https,
        "tier": "Uncataloged Source",
        "is_satire": False,
        "explanation": f"Source domain is '{domain}'. Independent fact-checking and cross-referencing recommended.",
    }
