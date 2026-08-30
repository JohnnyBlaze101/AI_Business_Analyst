import pandas as pd


def calculate_confidence(
    correlation,
    evidence_score,
    history_count,
    data_fresh,
    data_complete,
    contradictory=False
):
    """
    Calculate a transparent confidence score.

    This score represents confidence in the evidence,
    NOT probability of causation.
    """

    # ---------------------------------------
    # 1. Historical evidence
    # ---------------------------------------

    correlation_score = abs(correlation)

    # ---------------------------------------
    # 2. Current evidence
    # ---------------------------------------

    current_evidence_score = evidence_score

    # ---------------------------------------
    # 3. Historical sample size
    # ---------------------------------------

    if history_count >= 12:
        history_score = 1.0
    elif history_count >= 6:
        history_score = 0.8
    elif history_count >= 3:
        history_score = 0.5
    else:
        history_score = 0.2

    # ---------------------------------------
    # 4. Data quality
    # ---------------------------------------

    freshness_score = 1.0 if data_fresh else 0.5

    completeness_score = (
        1.0 if data_complete else 0.4
    )

    contradiction_score = (
        0.2 if contradictory else 1.0
    )

    # ---------------------------------------
    # 5. Combine evidence
    # ---------------------------------------

    confidence = (
        0.30 * correlation_score
        + 0.30 * current_evidence_score
        + 0.15 * history_score
        + 0.10 * freshness_score
        + 0.10 * completeness_score
        + 0.05 * contradiction_score
    )

    # Convert to percentage
    confidence_percentage = confidence * 100

    return confidence_percentage


def classify_confidence(confidence):
    """
    Convert numerical confidence into a
    human-readable category.
    """

    if confidence >= 75:
        return "High"

    elif confidence >= 50:
        return "Medium"

    else:
        return "Low"


def should_abstain(confidence):
    """
    Abstain when evidence confidence is below
    the minimum threshold required for attribution.
    """

    return confidence < 60

def get_confidence_reason(
    confidence,
    history_count,
    data_fresh,
    data_complete,
    contradictory
):
    """
    Explain why confidence is high, medium or low.
    """

    reasons = []

    if history_count < 6:
        reasons.append(
            "Limited historical data"
        )

    if not data_fresh:
        reasons.append(
            "Data may be stale"
        )

    if not data_complete:
        reasons.append(
            "Missing or incomplete data"
        )

    if contradictory:
        reasons.append(
            "Evidence is contradictory"
        )

    if confidence < 60:
        reasons.append(
            "Overall evidence is insufficient"
        )

    if not reasons:
        reasons.append(
            "Evidence is sufficiently consistent"
        )

    return reasons


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    confidence = calculate_confidence(
        correlation=0.99,
        evidence_score=0.90,
        history_count=8,
        data_fresh=True,
        data_complete=True,
        contradictory=False
    )

    category = classify_confidence(
        confidence
    )

    abstain = should_abstain(
        confidence
    )

    print("\nCONFIDENCE ANALYSIS")
    print("--------------------")

    print(
        f"Confidence: {confidence:.2f}%"
    )

    print(
        f"Category: {category}"
    )

    print(
        f"Abstain: {abstain}"
    )
