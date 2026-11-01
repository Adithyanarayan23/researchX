from typing import List, Dict, Any


def source_diversity(sources: List[Dict[str, Any]]) -> float:
    """
    Evaluates domain heterogeneity across collected sources.
    Higher diversity prevents single-domain echo chambers.
    """
    if not sources:
        return 0.0

    domains = set(s.get("domain") for s in sources if s.get("domain"))
    ratio = len(domains) / len(sources)
    return round(min(1.0, ratio), 4)


def source_quality(sources: List[Dict[str, Any]]) -> float:
    """
    Calculates average system credibility score across retrieved sources.
    """
    if not sources:
        return 0.0

    scores = [float(s.get("credibility_score", 0.70)) for s in sources]
    return round(sum(scores) / len(scores), 4)


def conflict_detection_rate(conflicts_detected: List[Dict[str, Any]], expected_has_conflict: bool) -> float:
    """
    Measures conflict detection accuracy against ground truth.
    """
    detected = len(conflicts_detected) > 0
    if expected_has_conflict == detected:
        return 1.0
    return 0.5 if not expected_has_conflict and detected else 0.0
