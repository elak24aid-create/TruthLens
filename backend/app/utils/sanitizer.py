import re
import html


def sanitize_text(raw_text: str) -> str:
    """
    Sanitizes user input text to prevent injection or malicious payloads.
    Strips raw HTML tags, unescapes entities, and normalizes excess whitespace.
    """
    if not raw_text:
        return ""

    # Unescape HTML entities first
    text = html.unescape(raw_text)

    # Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove non-printable control characters except standard whitespace
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ch == "\r" or ch >= " ")

    # Normalize excessive spaces (preserve single newlines)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)

    return text.strip()
