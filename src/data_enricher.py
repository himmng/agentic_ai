import os
import json
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# --------------------------------------------------
# Project paths (robust, no cwd nonsense)
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]   # agentic_ai/
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"
ENRICHED_DIR = DATA_DIR / "enriched"

ENRICHED_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = ENRICHED_DIR / "synergy_ai_enriched.jsonl"
EXTRACTED_FILE = EXTRACTED_DIR / "synergy_extracted.jsonl"

# --------------------------------------------------
# Load environment variables (ONE line, always works)
# --------------------------------------------------
load_dotenv(PROJECT_ROOT / ".env")

# --------------------------------------------------
# File-backed "API" (mimics real API cleanly)
# --------------------------------------------------
def load_jsonl_from_api(_unused_url: str = None):
    """
    Mimics an API call but reads from extracted JSONL.
    Keeps interface identical to real API.
    """
    if not EXTRACTED_FILE.exists():
        print(f"Extracted file not found: {EXTRACTED_FILE}")
        return []

    records = []
    with open(EXTRACTED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

# --------------------------------------------------
# Load already enriched IDs (idempotency)
# --------------------------------------------------
def load_seen_ids():
    if not OUTPUT_FILE.exists():
        return set()

    seen = set()
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                seen.add(json.loads(line)["id"])
            except Exception:
                continue
    return seen

# --------------------------------------------------
# Azure AI setup
# --------------------------------------------------
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
CSI_AGENT_NAME = os.getenv("CSI_AGENT")

if not PROJECT_ENDPOINT or not CSI_AGENT_NAME:
    raise ValueError("PROJECT_ENDPOINT or CSI_AGENT not set in .env")

credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential
)
openai_client = project_client.get_openai_client()

# --------------------------------------------------
# Call CSI Agent
# --------------------------------------------------
def call_csi_agent(records: list):
    conversation = openai_client.conversations.create()

    response = openai_client.responses.create(
        conversation=conversation.id,
        input=json.dumps(records, ensure_ascii=False),
        extra_body={
            "agent": {
                "name": CSI_AGENT_NAME,
                "type": "agent_reference"
            }
        }
    )

    try:
        return json.loads(response.output_text.strip())
    except Exception as e:
        raise RuntimeError(f"Failed to parse CSI agent output: {e}")

# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    print("Loading extracted data (API-mimic)...")
    extracted_data = load_jsonl_from_api()

    if not extracted_data:
        print("No extracted data found. Exiting.")
        exit(0)

    seen_ids = load_seen_ids()
    new_records = [r for r in extracted_data if r.get("id") not in seen_ids]

    if not new_records:
        print("No new records to enrich.")
        exit(0)

    print(f"Sending {len(new_records)} records to CSI agent...")
    enriched_records = call_csi_agent(new_records)

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for record in enriched_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Saved {len(enriched_records)} enriched records → {OUTPUT_FILE}")
