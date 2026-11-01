import re
from typing import List, Dict, Any


def context_relevance(query: str, retrieved_snippets: List[str]) -> float:
    """
    Measures lexical and semantic density of query concepts in retrieved snippets.
    """
    if not query or not retrieved_snippets:
        return 0.0

    query_tokens = set(re.findall(r"\w+", query.lower()))
    if not query_tokens:
        return 0.0

    scores = []
    for snip in retrieved_snippets:
        snip_tokens = set(re.findall(r"\w+", snip.lower()))
        matched = query_tokens.intersection(snip_tokens)
        scores.append(len(matched) / len(query_tokens))

    return round(sum(scores) / len(scores), 4) if scores else 0.0


def context_completeness(expected_topics: List[str], retrieved_snippets: List[str]) -> float:
    """
    Measures percentage of expected research topics covered by retrieved snippets.
    """
    if not expected_topics:
        return 1.0
    if not retrieved_snippets:
        return 0.0

    combined_text = " ".join(retrieved_snippets).lower()
    covered = 0
    for topic in expected_topics:
        if topic.lower() in combined_text:
            covered += 1

    return round(covered / len(expected_topics), 4)


def faithfulness(claims: List[Dict[str, Any]], retrieved_snippets: List[str]) -> float:
    """
    Assesses the proportion of claims whose text is corroborated by retrieved snippets.
    """
    if not claims:
        return 1.0
    if not retrieved_snippets:
        return 0.0

    verified_count = 0
    for c in claims:
        status = c.get("status", "").lower()
        if status in ("verified", "partially_verified"):
            verified_count += 1

    return round(verified_count / len(claims), 4)
