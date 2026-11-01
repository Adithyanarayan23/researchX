import ipaddress
import re
import socket
from urllib.parse import urlparse
from typing import Tuple


# Common prompt injection triggers found in wild web pages or malicious files
INJECTION_PATTERNS = [
    re.compile(r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b"),
    re.compile(r"(?i)\bdisregard\s+(all\s+)?(previous|prior)\s+(rules|prompts|instructions)\b"),
    re.compile(r"(?i)\byou\s+are\s+now\s+(an\s+unrestricted|a\s+different|in\s+developer\s+mode)\b"),
    re.compile(r"(?i)\breveal\s+(your\s+)?(system\s+prompt|secret\s+key|internal\s+instructions)\b"),
    re.compile(r"(?i)\bprint\s+(the\s+)?(full\s+)?system\s+prompt\b"),
    re.compile(r"(?i)\bforget\s+all\s+previous\s+directives\b"),
    re.compile(r"(?i)<\|im_start\|>|<\|im_end\|>|\[INST\]|\[/INST\]"),
    re.compile(r"(?i)assistant\s+must\s+output:\s*['\"].*['\"]"),
]

HTML_TAG_CLEANER = re.compile(r"<[^>]+>")


def sanitize_untrusted_content(raw_text: str) -> Tuple[str, bool]:
    """
    Sanitizes untrusted web or document text to prevent prompt injection and extract
    safe, neutral factual content.
    Returns: (sanitized_text, injection_detected_bool)
    """
    if not raw_text:
        return "", False

    # Strip dangerous HTML / Script / Style tags
    cleaned = HTML_TAG_CLEANER.sub(" ", raw_text)

    # Check for known injection patterns
    injection_found = False
    for pattern in INJECTION_PATTERNS:
        if pattern.search(cleaned):
            injection_found = True
            cleaned = pattern.sub("[REDACTED_POTENTIAL_INJECTION_TRIGGER]", cleaned)

    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned, injection_found


def is_safe_url(url: str) -> bool:
    """
    Validates URL to protect against SSRF (Server-Side Request Forgery).
    Rejects private IPs, loopback, link-local, AWS/GCP metadata endpoints.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        hostname_lower = hostname.lower()
        if hostname_lower in ("localhost", "metadata.google.internal"):
            return False

        # Resolve hostname to check for private or reserved IPs
        try:
            ip_str = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_str)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip_str == "169.254.169.254"
            ):
                return False
        except socket.error:
            # If domain can't be resolved, reject or mark unsafe
            return False

        return True
    except Exception:
        return False
