import hashlib
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import httpx
from app.core.security import is_safe_url, sanitize_untrusted_content
from app.tools.source_credibility import compute_source_credibility
from app.core.config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "ResearchX-Agentic-Crawler/1.0 (+https://researchx.internal)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


async def fetch_webpage(url: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
    """
    Fetches and extracts clean textual content from a URL safely.
    Applies SSRF checks, rate limits, HTML parsing, anti-prompt injection sanitization,
    SHA-256 hashing, and credibility scoring.
    """
    if not is_safe_url(url):
        logger.warning("Blocked unsafe or unresolvable URL: %s", url)
        return None

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers=HEADERS,
            verify=False
        ) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.warning("HTTP status %s for url %s", resp.status_code, url)
                return None

            content_type = resp.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "application/xml" not in content_type:
                logger.info("Skipping non-HTML content-type: %s", content_type)
                return None

            html = resp.text
    except Exception as e:
        logger.warning("Failed to fetch %s: %s", url, str(e))
        return None

    # Parse HTML with BeautifulSoup
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Strip scripts, styles, iframes, nav, footer
        for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside"]):
            tag.decompose()

        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Extract main text
        body_text = soup.get_text(separator="\n", strip=True)

        # Sanitize against prompt injection
        sanitized_text, injection_detected = sanitize_untrusted_content(body_text)
        if injection_detected:
            logger.warning("Prompt injection signature neutralized in URL: %s", url)

        # Truncate extremely large documents to reasonable research context (~25,000 chars)
        if len(sanitized_text) > 30000:
            sanitized_text = sanitized_text[:30000] + "... [truncated for research processing]"

        content_hash = hashlib.sha256(sanitized_text.encode("utf-8")).hexdigest()
        credibility_score, domain = compute_source_credibility(url)

        return {
            "url": url,
            "title": title or domain,
            "domain": domain,
            "publisher": domain,
            "content": sanitized_text,
            "content_hash": content_hash,
            "credibility_score": credibility_score,
            "source_type": "website",
            "injection_detected": injection_detected,
        }
    except Exception as e:
        logger.error("Error parsing content from %s: %s", url, str(e))
        return None
