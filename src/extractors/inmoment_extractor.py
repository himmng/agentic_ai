from typing import List, Dict

def extract_relevant_fields_inmoment(surveys: List[Dict]) -> List[Dict]:
    """
    Extract AI-ready fields from InMoment survey data for:
    - Sentiment analysis
    - Recommendations
    - Summary generation
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
        combined_text = " ".join(answer_texts)

        # --- Scores by category ---
        scores_by_category = {
            sc.get("criterion", "").lower(): sc.get("value")
            for sc in s.get("scores", [])
            if sc.get("criterion") and sc.get("value") is not None
        }

        # --- Tags ---
        tags = s.get("tags", {})

        # --- Incidents ---
        incidents = [
            {
                "type": inc.get("type"),
                "description": inc.get("description")
            }
            for inc in s.get("incidents", [])
        ]

        # --- Metadata / end user properties ---
        end_user_props = s.get("end_user_properties", {})
        metadata = {
            "survey_id": s.get("surveyId"),
            "survey_name": s.get("surveyName"),
            "customer_type": end_user_props.get("customer_type"),
            "region": end_user_props.get("region"),
            "tenure_years": end_user_props.get("tenure_years"),
            "device_type": s.get("deviceType"),
            "language": s.get("languageCode"),
            "organization": s.get("organizationName"),
            "mode": s.get("mode")
        }

        # --- Build final extracted object ---
        survey_obj = {
            "customer_id": s.get("contactId") or s.get("contact", {}).get("id"),
            "answer_texts": answer_texts,
            "combined_text": combined_text,
            "scores_by_category": scores_by_category,
            "tags": tags,
            "incidents": incidents,
            "metadata": metadata
        }

        extracted.append(survey_obj)

    return extracted
