import math
import re
from typing import List, Dict, Any, Optional
import numpy as np
from app.core.config import settings


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    if not vec_a or not vec_b:
        return 0.0
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    val = float(dot / (norm_a * norm_b))
    # Normalize from [-1, 1] to [0, 1]
    return max(0.0, min(1.0, (val + 1.0) / 2.0))


def keyword_match_score(query: str, text: str) -> float:
    """
    Computes keyword matching score based on token overlap and term density.
    Normalized to [0.0, 1.0].
    """
    if not query or not text:
        return 0.0

    tokens_query = set(re.findall(r"\w+", query.lower()))
    if not tokens_query:
        return 0.0

    tokens_text = re.findall(r"\w+", text.lower())
    if not tokens_text:
        return 0.0

    text_token_set = set(tokens_text)
    matched = tokens_query.intersection(text_token_set)
    overlap_ratio = len(matched) / len(tokens_query)

    # Frequency factor
    freq_count = sum(tokens_text.count(token) for token in matched)
    density = min(1.0, freq_count / (len(tokens_text) + 1) * 10)

    score = 0.7 * overlap_ratio + 0.3 * density
    return max(0.0, min(1.0, score))


def hybrid_search(
    query: str,
    query_embedding: List[float],
    candidate_chunks: List[Dict[str, Any]],
    top_k: int = 5,
    semantic_weight: Optional[float] = None,
    keyword_weight: Optional[float] = None,
    quality_weight: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Executes hybrid retrieval combining:
    final_score = w_semantic * semantic_score + w_keyword * keyword_score + w_quality * source_quality_score
    Returns ranked evidence chunks with individual component scores and final_score.
    """
    w_sem = semantic_weight if semantic_weight is not None else settings.RAG_SEMANTIC_WEIGHT
    w_key = keyword_weight if keyword_weight is not None else settings.RAG_KEYWORD_WEIGHT
    w_qual = quality_weight if quality_weight is not None else settings.RAG_QUALITY_WEIGHT

    # Normalize weights if sum != 1.0
    total_w = w_sem + w_key + w_qual
    if total_w > 0:
        w_sem /= total_w
        w_key /= total_w
        w_qual /= total_w

    scored_candidates = []

    for item in candidate_chunks:
        content = item.get("content", "")
        item_embedding = item.get("embedding", [])
        source_quality = float(item.get("credibility_score", 0.70))

        # 1. Semantic score
        sem_score = cosine_similarity(query_embedding, item_embedding) if item_embedding else 0.50

        # 2. Keyword score
        key_score = keyword_match_score(query, content)

        # 3. Final composite score
        final_score = (w_sem * sem_score) + (w_key * key_score) + (w_qual * source_quality)

        scored_item = dict(item)
        scored_item["semantic_score"] = round(sem_score, 4)
        scored_item["keyword_score"] = round(key_score, 4)
        scored_item["quality_score"] = round(source_quality, 4)
        scored_item["final_score"] = round(final_score, 4)

        scored_candidates.append(scored_item)

    # Sort descending by final_score
    scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
    return scored_candidates[:top_k]
