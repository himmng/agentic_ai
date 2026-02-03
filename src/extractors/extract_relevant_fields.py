from typing import List, Dict


def extract_relevant_fields(surveys: List[Dict]) -> List[Dict]:
    """
    Extracts AI-ready analytical fields from InMoment survey data.
    Designed for sentiment analysis and fusion with FullStory signals.
    """

    extracted = []

    for s in surveys:

        # --- FILTERING RULES ---
        if not s.get("complete", False):
            continue
        if s.get("exclusionReason"):
            continue

        # --- ANSWERS ---
        answers = s.get("answers", [])
        answer_texts = []
        answer_scores = []

        for a in answers:
            if a.get("text"):
                answer_texts.append(a.get("text"))
            if a.get("score") is not None:
                answer_scores.append(a.get("score"))

        combined_text = " ".join(answer_texts)

        # --- TAGS ---
        tags = []
        for t in s.get("tags", []):
            if isinstance(t, dict) and t.get("name"):
                tags.append(t["name"])

        # --- SCORES BY CATEGORY ---
        scores_by_category = {}
        for sc in s.get("scores", []):
            if sc.get("name") and sc.get("score") is not None:
                scores_by_category[sc["name"].lower()] = sc["score"]

        # --- INCIDENT SIGNALS ---
        incident_types = []
        for inc in s.get("incidents", []):
            if inc.get("type"):
                incident_types.append(inc["type"].lower())

        # --- METADATA ---
        metadata = {
            "mode": s.get("mode"),
            "device_type": s.get("deviceType"),
            "language": s.get("languageCode"),
            "organization": s.get("organizationName"),
            "customer_region": s.get("end_user", {})
                .get("properties", {})
                .get("region"),
            "customer_type": s.get("end_user", {})
                .get("properties", {})
                .get("customer_type"),
            "tenure_years": s.get("end_user", {})
                .get("properties", {})
                .get("tenure_years")
        }

        survey_obj = {
            "id": s.get("id"),
            "survey_id": s.get("surveyId"),
            "overall_score": scores_by_category.get("overall experience"),
            "answer_texts": answer_texts,
            "answer_scores": answer_scores,
            "combined_text": combined_text,
            "tags": tags,
            "scores_by_category": scores_by_category,
            "incident_types": incident_types,
            "metadata": metadata
        }

        extracted.append(survey_obj)

    return extracted
