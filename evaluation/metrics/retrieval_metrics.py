from typing import List, Set, Any


def precision_at_k(retrieved_snippets: List[str], expected_entities: List[str], k: int = 5) -> float:
    """
    Computes Precision@K: Fraction of top-K retrieved snippets containing at least one expected entity.
    """
    if not retrieved_snippets or not expected_entities or k <= 0:
        return 0.0

    top_k = retrieved_snippets[:k]
    matched_count = 0

    expected_lower = [e.lower() for e in expected_entities]

    for snippet in top_k:
        snip_lower = snippet.lower()
        if any(ent in snip_lower for ent in expected_lower):
            matched_count += 1

    return round(matched_count / len(top_k), 4)


def recall_at_k(retrieved_snippets: List[str], expected_entities: List[str], k: int = 5) -> float:
    """
    Computes Recall@K: Fraction of expected entities captured across top-K retrieved snippets.
    """
    if not retrieved_snippets or not expected_entities or k <= 0:
        return 0.0

    combined_text = " ".join(retrieved_snippets[:k]).lower()
    found_entities = 0

    for ent in expected_entities:
        if ent.lower() in combined_text:
            found_entities += 1

    return round(found_entities / len(expected_entities), 4)
