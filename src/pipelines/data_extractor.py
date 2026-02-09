import json
import requests
from pathlib import Path
from typing import List, Dict
from src.config.paths import EXTRACTED_DATA_DIR, FIELD_EXTRACTION_CONFIG_DIR

# --------------------------------------------------
# Config paths
# --------------------------------------------------
FIELDS_CONFIG_FILE = FIELD_EXTRACTION_CONFIG_DIR / "fields_to_extract.json"
OUTPUT_FILE = EXTRACTED_DATA_DIR / "synergy_extracted.jsonl"
EXTRACTED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# API URLs (local dev simulation)
# --------------------------------------------------
INMOMENT_API_URL = "http://127.0.0.1:8080/data/raw/synergy_inmoment.json"
FULLSTORY_API_URL = "http://127.0.0.1:8080/data/raw/synergy_fullstory.json"

# --------------------------------------------------
# Load fields configuration
# --------------------------------------------------
with FIELDS_CONFIG_FILE.open("r", encoding="utf-8") as f:
    fields_to_extract = json.load(f)
INMOMENT_FIELDS = fields_to_extract.get("inmoment", [])
FULLSTORY_FIELDS = fields_to_extract.get("fullstory", [])

# --------------------------------------------------
# Fetch JSON via API
# --------------------------------------------------
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

# --------------------------------------------------
# Generic extractor based on fields config
# --------------------------------------------------
def extract_fields(records: List[Dict], fields: List[str]) -> List[Dict]:
    extracted = []
    for r in records:
        extracted.append({k: r.get(k) for k in fields})
    return extracted

# --------------------------------------------------
# Merge datasets by customer ID
# --------------------------------------------------
def merge_datasets(inmoment_data: List[Dict], fullstory_data: List[Dict]) -> List[Dict]:
    inmoment_lookup = {str(d.get("id") or d.get("customer_id")): d for d in inmoment_data}
    fullstory_lookup = {str(d.get("customer_id") or d.get("id")): d for d in fullstory_data}

    all_ids = set(inmoment_lookup.keys()).union(fullstory_lookup.keys())
    enriched_data = []

    for cust_id in all_ids:
        combined = {
            "id": cust_id,
            "inmoment": inmoment_lookup.get(cust_id, {}),
            "fullstory": fullstory_lookup.get(cust_id, {})
        }
        enriched_data.append(combined)

    return enriched_data

# --------------------------------------------------
# Save JSONL safely
# --------------------------------------------------
def save_as_jsonl(data: List[Dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Saved enriched JSONL data to {path} ({len(data)} records)")

# --------------------------------------------------
# Main runner
# --------------------------------------------------
def main():
    # Fetch data via API
    inmoment_raw = fetch_json_via_api(INMOMENT_API_URL)
    fullstory_raw = fetch_json_via_api(FULLSTORY_API_URL)

    # Extract only configured fields
    inmoment_extracted = extract_fields(inmoment_raw, INMOMENT_FIELDS)
    fullstory_extracted = extract_fields(fullstory_raw, FULLSTORY_FIELDS)

    # Merge datasets
    enriched_data = merge_datasets(inmoment_extracted, fullstory_extracted)

    # Save output
    save_as_jsonl(enriched_data, OUTPUT_FILE)

if __name__ == "__main__":
    main()
