import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from src.config.paths import ENV, EXTRACTED_DATA_DIR, ENRICHED_DATA_DIR

# --------------------------------------------------
# Setup paths
# --------------------------------------------------
ENRICHED_DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = ENRICHED_DATA_DIR / "synergy_enriched.jsonl"
EXTRACTED_FILE = EXTRACTED_DATA_DIR / "synergy_extracted.jsonl"

# --------------------------------------------------
# Load environment
# --------------------------------------------------
load_dotenv(ENV)
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
CSI_AGENT_NAME = os.getenv("CSI_AGENT")

if not PROJECT_ENDPOINT or not CSI_AGENT_NAME:
    raise ValueError("PROJECT_ENDPOINT or CSI_AGENT not set in .env")

# --------------------------------------------------
# Azure AI client
# --------------------------------------------------
project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)
openai_client = project_client.get_openai_client()

# --------------------------------------------------
# File-backed API
# --------------------------------------------------
def load_jsonl_from_api() -> list[dict]:
    if not EXTRACTED_FILE.exists():
        print(f"Extracted file not found: {EXTRACTED_FILE}")
        return []
    records = []
    with EXTRACTED_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

# --------------------------------------------------
# Already enriched IDs (idempotency)
# --------------------------------------------------
def load_seen_ids() -> set[str]:
    if not OUTPUT_FILE.exists():
        return set()
    seen = set()
    with OUTPUT_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                seen.add(json.loads(line)["id"])
            except Exception:
                continue
    return seen

# --------------------------------------------------
# Call CSI agent for ONE record
# --------------------------------------------------
def call_csi_agent_single(record: dict) -> dict:
    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=json.dumps(record, ensure_ascii=False),
        extra_body={"agent": {"name": CSI_AGENT_NAME, "type": "agent_reference"}}
    )

    try:
        parsed = json.loads(response.output_text.strip())
        # Robust handling
        if isinstance(parsed, dict):
            return parsed
        elif isinstance(parsed, list):
            if len(parsed) == 1 and isinstance(parsed[0], dict):
                return parsed[0]
            elif len(parsed) > 1:
                # Agent returned multiple objects for a single record: log and take first
                print(f"WARNING: CSI agent returned multiple objects for record id={record.get('id')}. Using first object.")
                return parsed[0]
            else:
                raise ValueError("CSI agent returned empty array")
        else:
            raise ValueError("CSI agent output is not a dict or array")
    except Exception as e:
        raise RuntimeError(f"Failed to parse CSI agent output for record id={record.get('id')}") from e

# --------------------------------------------------
# Parallel enrichment
# --------------------------------------------------
def enrich_records_parallel(records: list[dict], max_workers: int = 10) -> list[dict]:
    enriched = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(call_csi_agent_single, r): r["id"] for r in records}
        for future in as_completed(futures):
            enriched.append(future.result())
    return enriched

# --------------------------------------------------
# Save enriched records
# --------------------------------------------------
def save_enriched_records(enriched_records: list[dict]):
    with OUTPUT_FILE.open("a", encoding="utf-8") as f:
        for record in enriched_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Saved {len(enriched_records)} enriched records → {OUTPUT_FILE}")

# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    print("Loading extracted data...")
    extracted_data = load_jsonl_from_api()
    if not extracted_data:
        print("No extracted data found. Exiting.")
        return

    seen_ids = load_seen_ids()
    new_records = [r for r in extracted_data if r.get("id") not in seen_ids]

    if not new_records:
        print("No new records to enrich.")
        return

    print(f"Enriching {len(new_records)} records in parallel...")
    enriched_records = enrich_records_parallel(new_records, max_workers=10)
    save_enriched_records(enriched_records)

if __name__ == "__main__":
    main()
