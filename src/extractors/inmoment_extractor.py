# src/extractors/inmoment_extractor.py

from typing import List, Dict

def extract_relevant_fields_inmoment(surveys: List[Dict]) -> List[Dict]:
    """
    Extracts AI-ready fields from InMoment survey data.
    Handles multiple answers, incidents, tags, scores, metadata, and social reviews.
    """

    extracted = []

    for s in surveys:
        # --- Skip incomplete or excluded surveys ---
        if not s.get("complete", False):
            continue
        if s.get("exclusionReason"):
            continue

        # --- Answers ---
        answers = s.get("answers", [])
        answer_texts = [a.get("text") for a in answers if a.get("text")]
        answer_scores = [a.get("score") for a in answers if a.get("score") is not None]
        combined_text = " ".join(answer_texts)

        # --- Scores by category ---
        scores_by_category = {sc["name"].lower(): sc["score"]
                              for sc in s.get("scores", [])
                              if sc.get("name") and sc.get("score") is not None}

        # --- Tags ---
        tags = [t.get("name") for t in s.get("tags", []) if t.get("name")]

        # --- Incidents ---
        incidents = [{"type": inc.get("type"),
                      "description": inc.get("description"),
                      "severity": inc.get("severity"),
                      "occurredAt": inc.get("occurredAt")}
                     for inc in s.get("incidents", [])]

        # --- Social review ---
        social_review = s.get("socialReview", {})

        # --- Metadata ---
        end_user = s.get("end_user", {}).get("properties", {})
        metadata = {
            "mode": s.get("mode"),
            "device_type": s.get("deviceType"),
            "language": s.get("languageCode"),
            "organization": s.get("organizationName"),
            "customer_region": end_user.get("region"),
            "customer_type": end_user.get("customer_type"),
            "tenure_years": end_user.get("tenure_years")
        }

        # --- Build extracted object ---
        extracted.append({
            "id": s.get("id"),
            "survey_id": s.get("surveyId"),
            "overall_score": scores_by_category.get("overall experience"),
            "answer_texts": answer_texts,
            "answer_scores": answer_scores,
            "combined_text": combined_text,
            "tags": tags,
            "scores_by_category": scores_by_category,
            "incidents": incidents,
            "social_review": social_review,
            "metadata": metadata
        })

    return extracted
