import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from src.config.paths import EXTRACTED_DATA_DIR, ENRICHED_DATA_DIR, ESCALATED_DATA_DIR

# --------------------------------------------------
# Setup paths
# --------------------------------------------------
ENRICHED_DATA_DIR.mkdir(parents=True, exist_ok=True)
ESCALATED_DATA_DIR.mkdir(parents=True, exist_ok=True)

EXTRACTED_FILE = EXTRACTED_DATA_DIR / "synergy_extracted.jsonl"
ENRICHED_FILE = ENRICHED_DATA_DIR / "synergy_enriched.jsonl"
ESCALATED_FILE = ESCALATED_DATA_DIR / "synergy_escalated.jsonl"

# --------------------------------------------------
# Load environment
# --------------------------------------------------
load_dotenv()
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
CSI_AGENT_NAME = os.getenv("CSI_AGENT")
ESCALATION_AGENT_NAME = os.getenv("ESCALATION_AGENT")

if not PROJECT_ENDPOINT or not CSI_AGENT_NAME or not ESCALATION_AGENT_NAME:
    raise ValueError("PROJECT_ENDPOINT, CSI_AGENT, or ESCALATION_AGENT not set in .env")

# --------------------------------------------------
# Azure AI client
# --------------------------------------------------
project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)
openai_client = project_client.get_openai_client()

# --------------------------------------------------
# Helper: Load JSONL
# --------------------------------------------------
def load_jsonl(file_path) -> list[dict]:
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return []
    records = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records

# --------------------------------------------------
# Helper: Already processed IDs
# --------------------------------------------------
def load_seen_ids(file_path) -> set[str]:
    if not file_path.exists():
        return set()
    seen = set()
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                seen.add(json.loads(line)["id"])
            except Exception:
                continue
    return seen

# --------------------------------------------------
# CSI Agent: enrich single record
# --------------------------------------------------
def call_csi_agent_single(record: dict) -> dict:
    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=json.dumps(record, ensure_ascii=False),
        extra_body={"agent": {"name": CSI_AGENT_NAME, "type": "agent_reference"}}
    )

    parsed = json.loads(response.output_text.strip())
    if isinstance(parsed, dict):
        return parsed
    elif isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], dict):
        return parsed[0]
    else:
        raise RuntimeError("CSI agent output must be a single JSON object or a single-item array")

# --------------------------------------------------
# Escalation Agent: tag single record
# --------------------------------------------------
def call_escalation_agent_single(record: dict) -> dict:
    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=json.dumps(record, ensure_ascii=False),
        extra_body={"agent": {"name": ESCALATION_AGENT_NAME, "type": "agent_reference"}}
    )

    try:
        parsed = json.loads(response.output_text.strip())
        # Handle single object or single-item array
        if isinstance(parsed, dict):
            return parsed
        elif isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], dict):
            return parsed[0]
        else:
            raise ValueError(
                "Escalation agent output must be a single JSON object or an array of length 1"
            )
    except Exception as e:
        raise RuntimeError("Failed to parse Escalation agent output") from e

# --------------------------------------------------
# Parallel processing
# --------------------------------------------------
def process_parallel(records: list[dict], agent_fn, max_workers: int = 10) -> list[dict]:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(agent_fn, r): r["id"] for r in records}
        for future in as_completed(futures):
            results.append(future.result())
    return results

# --------------------------------------------------
# Save JSONL
# --------------------------------------------------
def save_jsonl(file_path, records: list[dict]):
    with file_path.open("a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Saved {len(records)} records → {file_path}")

# --------------------------------------------------
# Main pipeline
# --------------------------------------------------
def main():
    #Load extracted data
    print("Loading extracted data...")
    extracted_data = load_jsonl(EXTRACTED_FILE)
    if not extracted_data:
        print("No extracted data found. Exiting.")
        return

    #Enrichment: skip already enriched
    seen_enriched = load_seen_ids(ENRICHED_FILE)
    to_enrich = [r for r in extracted_data if r.get("id") not in seen_enriched]

    if to_enrich:
        print(f"Enriching {len(to_enrich)} records in parallel...")
        enriched_records = process_parallel(to_enrich, call_csi_agent_single, max_workers=10)
        save_jsonl(ENRICHED_FILE, enriched_records)
    else:
        print("No new records to enrich.")
        enriched_records = load_jsonl(ENRICHED_FILE)

    #Escalation tagging: skip already escalated
    seen_escalated = load_seen_ids(ESCALATED_FILE)
    to_escalate = [r for r in enriched_records if r.get("id") not in seen_escalated]

    if to_escalate:
        print(f"Escalating {len(to_escalate)} records in parallel...")
        escalated_records = process_parallel(to_escalate, call_escalation_agent_single, max_workers=10)
        save_jsonl(ESCALATED_FILE, escalated_records)
    else:
        print("No new records to escalate.")

if __name__ == "__main__":
    main()