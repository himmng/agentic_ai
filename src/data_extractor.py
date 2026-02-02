import json
import requests
from pathlib import Path
from typing import List, Dict

# -----------------------------
# Project and data paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[0]
DATA_DIR = PROJECT_ROOT.parent / "data" / "raw"
PROCESSED_FILE = PROJECT_ROOT.parent / "data" / "augmented" / "synergy_inmoment_processed.json"
PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Config
# -----------------------------
LOCAL_API_URL = "http://127.0.0.1:8080/synergy_inmoment.json"
RAW_FILE = DATA_DIR / "synergy_inmoment.json"

# -----------------------------
# Load previously processed IDs
# -----------------------------
def load_seen_ids() -> set:
    if not PROCESSED_FILE.exists():
        return set()
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        processed_data = json.load(f)
    return {s["id"] for s in processed_data}

# -----------------------------
# Fetch raw data from API or fallback to file
# -----------------------------
def fetch_raw_data() -> List[Dict]:
    try:
        print(f"Fetching data from API: {LOCAL_API_URL}")
        response = requests.get(LOCAL_API_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API fetch failed ({e}), falling back to local file: {RAW_FILE}")
        if not RAW_FILE.exists():
            print("Raw file not found!")
            return []
        with open(RAW_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

# -----------------------------
# Extract relevant fields
# -----------------------------
def extract_relevant_fields(surveys: List[Dict]) -> List[Dict]:
    extracted = []
    for s in surveys:
        if not s.get("complete", False):
            continue
        if s.get("exclusionReason"):
            continue
        survey_obj = {
            "id": s.get("id"),
            "survey_id": s.get("surveyId"),
            "score": s.get("scores")[0]["score"] if s.get("scores") else None,
            "text": s.get("answers")[0]["text"] if s.get("answers") else "",
            "tags": [t["tag"] for t in s.get("tags", []) if t.get("tag")],
        }
        extracted.append(survey_obj)
    return extracted

# -----------------------------
# Incremental loader
# -----------------------------
def incremental_load():
    seen_ids = load_seen_ids()
    raw_data = fetch_raw_data()
    extracted = extract_relevant_fields(raw_data)
    new_surveys = [s for s in extracted if s["id"] not in seen_ids]

    if not new_surveys:
        print("No new survey responses found.")
        return

    # Append new surveys to processed file
    if PROCESSED_FILE.exists():
        with open(PROCESSED_FILE, "r+", encoding="utf-8") as f:
            processed_data = json.load(f)
            processed_data.extend(new_surveys)
            f.seek(0)
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
            f.truncate()
    else:
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            json.dump(new_surveys, f, indent=2, ensure_ascii=False)

    print(f"Processed {len(new_surveys)} new survey responses. Total saved: {len(new_surveys) + len(seen_ids)}")

# -----------------------------
# Run manually
# -----------------------------
if __name__ == "__main__":
    incremental_load()
