# src/data_extractor.py

import json
import requests
from pathlib import Path
from typing import List, Dict

# Import the extractors
from .extractors.inmoment_extractor import extract_relevant_fields_inmoment
from .extractors.fullstory_extractor import extract_relevant_fields_fullstory

# -----------------------------
# File paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extracted"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# API URLs (simulate request)
INMOMENT_API_URL = f"http://127.0.0.1:8080/data/raw/synergy_inmoment.json"
FULLSTORY_API_URL = f"http://127.0.0.1:8080/data/raw/synergy_fullstory.json"

OUTPUT_FILE = OUTPUT_DIR / "synergy_extracted.jsonl"

# -----------------------------
# Fetch JSON via requests
# -----------------------------
def fetch_json_via_api(url: str) -> List[Dict]:
    try:
        print(f"Fetching data from API: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"API fetch failed ({e})")
        return []

# -----------------------------
# Merge datasets by customer id
# -----------------------------
def merge_datasets(inmoment_data: List[Dict], fullstory_data: List[Dict]) -> List[Dict]:
    inmoment_lookup = {str(d.get("id") or d.get("customer_id")): d for d in inmoment_data}
    fullstory_lookup = {str(d.get("customer_id") or d.get("id")): d for d in fullstory_data}

    all_ids = set(inmoment_lookup.keys()).union(fullstory_lookup.keys())
    enriched_data = []

    for cust_id in all_ids:
        inmoment_rec = inmoment_lookup.get(cust_id, {})
        fullstory_rec = fullstory_lookup.get(cust_id, {})

        combined = {
            "id": cust_id,
            "inmoment": {
                "survey_id": inmoment_rec.get("survey_id"),
                "overall_score": inmoment_rec.get("overall_score"),
                "answer_texts": inmoment_rec.get("answer_texts", []),
                "answer_scores": inmoment_rec.get("answer_scores", []),
                "combined_text": inmoment_rec.get("combined_text", ""),
                "tags": inmoment_rec.get("tags", []),
                "scores_by_category": inmoment_rec.get("scores_by_category", {}),
                "incident_types": inmoment_rec.get("incident_types", []),
                "metadata": inmoment_rec.get("metadata", {})
            } if inmoment_rec else {},
            "fullstory": {
                "session_id": fullstory_rec.get("session_id"),
                "platform": fullstory_rec.get("platform"),
                "region": fullstory_rec.get("region"),
                "session_start_time": fullstory_rec.get("session_start_time"),
                "session_end_time": fullstory_rec.get("session_end_time"),
                "signals": fullstory_rec.get("signals", []),
                "journey_steps": fullstory_rec.get("journey_steps", []),
                "journey_summary": fullstory_rec.get("journey_summary", "")
            } if fullstory_rec else {}
        }

        enriched_data.append(combined)

    return enriched_data

# -----------------------------
# Save as JSONL
# -----------------------------
def save_as_jsonl(data: List[Dict], path: Path):
    with open(path, "w", encoding="utf-8") as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Saved enriched JSONL data to {path} ({len(data)} records)")

# -----------------------------
# Main runner
# -----------------------------
if __name__ == "__main__":

    # Fetch data via API
    inmoment_raw = fetch_json_via_api(INMOMENT_API_URL)
    fullstory_raw = fetch_json_via_api(FULLSTORY_API_URL)

    # Extract relevant fields
    inmoment_extracted = extract_relevant_fields_inmoment(inmoment_raw)
    fullstory_extracted = extract_relevant_fields_fullstory(fullstory_raw)

    # Merge by customer id (overwrite-safe)
    enriched_data = merge_datasets(inmoment_extracted, fullstory_extracted)

    # Save as JSONL
    save_as_jsonl(enriched_data, OUTPUT_FILE)
