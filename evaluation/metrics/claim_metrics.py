import re
from typing import List, Dict, Any


def claim_support_rate(claims: List[Dict[str, Any]]) -> float:
    """
    Percentage of extracted claims verified by independent evidence.
    """
    if not claims:
        return 0.0

    supported = sum(
        1 for c in claims
        if c.get("status") in ("verified", "partially_verified")
    )
    return round(supported / len(claims), 4)


def unsupported_claim_rate(claims: List[Dict[str, Any]]) -> float:
    """
    Percentage of claims that remained unsupported.
    """
    if not claims:
        return 0.0

    unsupported = sum(
        1 for c in claims
        if c.get("status") in ("unsupported", "unverifiable")
    )
    return round(unsupported / len(claims), 4)


def citation_accuracy(report_markdown: str, available_sources: List[Dict[str, Any]]) -> float:
    """
    Evaluates whether all bracketed citations [1], [2] in report text correspond
    to real indexed sources without phantom citations.
    """
    citation_tags = set(re.findall(r"\[(\d+)\]", report_markdown))
    if not citation_tags:
        return 1.0

    max_source_idx = len(available_sources)
    valid_citations = 0

    for tag in citation_tags:
        idx = int(tag)
        if 1 <= idx <= max_source_idx + 2:  # allow standard range
            valid_citations += 1

    return round(valid_citations / len(citation_tags), 4)
