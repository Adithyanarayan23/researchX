from urllib.parse import urlparse
from typing import Tuple

# Domain classification rules (matches Section 13)
GOV_EDU_DOMAINS = {".gov", ".edu", ".mil", ".org.in", ".ac.uk", ".gov.in"}

TIER_1_SOURCES = {
    # High-reputation research, filing, or standards bodies
    "sec.gov", "arxiv.org", "nature.com", "ieee.org", "acm.org", "nih.gov",
    "reuters.com", "bloomberg.com", "ft.com", "wsj.com", "apnews.com"
}

TIER_2_SOURCES = {
    # Reputable tech & business journalism
    "techcrunch.com", "venturebeat.com", "theverge.com", "wired.com",
    "cnbc.com", "forbes.com", "economist.com", "arstechnica.com",
    "semianalysis.com", "anandtech.com"
}

TIER_3_OFFICIAL_CORP = {
    # Official vendor documentation / company sites
    "nvidia.com", "amd.com", "intel.com", "openai.com", "microsoft.com",
    "google.com", "deepmind.google", "anthropic.com", "aws.amazon.com",
    "cloud.google.com", "azure.microsoft.com", "github.com"
}


def compute_source_credibility(
    url: str,
    source_type: str = "website",
    has_author_or_date: bool = True
) -> Tuple[float, str]:
    """
    Computes a system source-quality score based on domain reputation,
    source type, and metadata presence.
    Returns: (credibility_score: float [0.0 - 1.0], domain: str)
    """
    if not url:
        return 0.70, "internal_document"

    try:
        parsed = urlparse(url)
        domain = (parsed.hostname or "").lower()
        if domain.startswith("www."):
            domain = domain[4:]
    except Exception:
        return 0.50, "unknown"

    score = 0.50  # Default baseline for web pages

    # 1. TLD inspection
    for ext in GOV_EDU_DOMAINS:
        if domain.endswith(ext):
            score = 0.95
            return score, domain

    # 2. Curated domains
    if domain in TIER_1_SOURCES or any(domain.endswith("." + d) for d in TIER_1_SOURCES):
        score = 0.92
    elif domain in TIER_3_OFFICIAL_CORP or any(domain.endswith("." + d) for d in TIER_3_OFFICIAL_CORP):
        score = 0.88
    elif domain in TIER_2_SOURCES or any(domain.endswith("." + d) for d in TIER_2_SOURCES):
        score = 0.82
    elif source_type in ("research_paper", "company_doc", "gov_report"):
        score = 0.85
    elif "blog" in domain or "medium.com" in domain or "substack.com" in domain:
        score = 0.55
    else:
        score = 0.65

    # 3. Adjust for metadata presence
    if has_author_or_date:
        score = min(1.0, score + 0.05)

    return round(score, 2), domain
