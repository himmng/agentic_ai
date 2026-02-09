import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from src.config.paths import (
    ENV,
    EXTRACTED_DATA_DIR,
    ENRICHED_DATA_DIR,
)

# --------------------------------------------------
# Paths (canonical, root-safe)
# --------------------------------------------------

ENRICHED_DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = ENRICHED_DATA_DIR / "synergy_enriched.jsonl"
EXTRACTED_FILE = EXTRACTED_DATA_DIR / "synergy_extracted.jsonl"

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv(ENV)

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
CSI_AGENT_NAME = os.getenv("CSI_AGENT")

if not PROJECT_ENDPOINT or not CSI_AGENT_NAME:
    raise ValueError("PROJECT_ENDPOINT or CSI_AGENT not set in .env")

# --------------------------------------------------
# Azure AI setup
# --------------------------------------------------

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

# --------------------------------------------------
# File-backed "API" (API-compatible abstraction)
# --------------------------------------------------

def load_jsonl_from_api(_unused_url: str | None = None) -> list[dict]:
    """
    Mimics an API call but reads from extracted JSONL.
    Keeps interface identical to real API.
    """
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
# Load already enriched IDs (idempotency)
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
# Call CSI Agent
# --------------------------------------------------

def call_csi_agent(records: list[dict]) -> list[dict]:
    conversation = openai_client.conversations.create()

    response = openai_client.responses.create(
        conversation=conversation.id,
        input=json.dumps(records, ensure_ascii=False),
        extra_body={
            "agent": {
                "name": CSI_AGENT_NAME,
                "type": "agent_reference",
            }
        },
    )

    try:
        parsed = json.loads(response.output_text.strip())
        if not isinstance(parsed, list):
            raise ValueError("CSI agent output must be a JSON array")
        return parsed
    except Exception as e:
        raise RuntimeError(f"Failed to parse CSI agent output") from e

# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    print("Loading extracted data (API-mimic)...")
    extracted_data = load_jsonl_from_api()

    if not extracted_data:
        print("No extracted data found. Exiting.")
        return

    seen_ids = load_seen_ids()
    new_records = [r for r in extracted_data if r.get("id") not in seen_ids]

    if not new_records:
        print("No new records to enrich.")
        return

    print(f"Sending {len(new_records)} records to CSI agent...")
    enriched_records = call_csi_agent(new_records)

    with OUTPUT_FILE.open("a", encoding="utf-8") as f:
        for record in enriched_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Saved {len(enriched_records)} enriched records → {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
