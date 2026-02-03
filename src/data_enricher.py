# src/ai_enricher.py

import os
from dotenv import load_dotenv
import json
import requests
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# -----------------------------
# Project paths
# -----------------------------
load_dotenv("./agents/.env")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "enriched"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "synergy_ai_enriched.jsonl"

# -----------------------------
# API URLs for raw/enriched data
# -----------------------------
RAW_DATA_API = {
    "extracted": "http://127.0.0.1:8080/data/extracted/synergy_extracted.jsonl"
}

# -----------------------------
# Load JSON from API
# -----------------------------
# -----------------------------
# Load JSONL from API
# -----------------------------
def load_jsonl_from_api(url: str):
    try:
        print(f"Fetching data from API: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = []
        for line in response.text.strip().splitlines():
            if line:
                data.append(json.loads(line))
        return data
    except Exception as e:
        print(f"API fetch failed ({e})")
        return []

# -----------------------------
# Azure AI client
# -----------------------------
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
if not PROJECT_ENDPOINT:
    raise ValueError("PROJECT_ENDPOINT not set in .env")

credential = DefaultAzureCredential()
project_client = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
openai_client = project_client.get_openai_client()

INMOMENT_AGENT_NAME = os.environ.get("INMOMENT_SURVEY_INTELLIGENCE_AGENT")
FULLSTORY_AGENT_NAME = os.environ.get("FULLSTORY_SIGNAL_EXTRACTOR_AGENT")

if not INMOMENT_AGENT_NAME or not FULLSTORY_AGENT_NAME:
    raise ValueError("Azure agent names not set in .env")

# -----------------------------
# Call Azure agent
# -----------------------------
def call_agent(agent_name: str, records: list):
    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=json.dumps(records, ensure_ascii=False),
        extra_body={"agent": {"name": agent_name, "type": "agent_reference"}}
    )
    try:
        return json.loads(response.output_text.strip())
    except Exception as e:
        print(f"Failed to parse AI output from {agent_name}: {e}")
        return []

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    # Fetch data from API
    inmoment_raw = load_jsonl_from_api(RAW_DATA_API["extracted"])
    fullstory_raw = load_jsonl_from_api(RAW_DATA_API["extracted"])


    if not inmoment_raw and not fullstory_raw:
        print("No data fetched from API. Exiting.")
        exit(0)

    # Call agents
    print("Calling InMoment AI agent...")
    inmoment_ai = call_agent(INMOMENT_AGENT_NAME, [{"id": r.get("id"), "extracted": r} for r in inmoment_raw])

    print("Calling FullStory AI agent...")
    fullstory_ai = call_agent(FULLSTORY_AGENT_NAME, [{"id": r.get("id") or r.get("customer_id"), "extracted": r} for r in fullstory_raw])

    # Merge AI outputs by id
    enriched_data = []
    all_ids = set([str(r["id"]) for r in inmoment_ai] + [str(r["id"]) for r in fullstory_ai])

    for cust_id in all_ids:
        inmoment_data = next((i.get("inmoment") for i in inmoment_ai if str(i["id"]) == cust_id), {})
        fullstory_data = next((f.get("fullstory") for f in fullstory_ai if str(f["id"]) == cust_id), {})

        enriched_data.append({
            "id": cust_id,
            "inmoment": inmoment_data,
            "fullstory": fullstory_data
        })

    # Save as JSONL
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for record in enriched_data:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Saved AI-enriched data to {OUTPUT_FILE} ({len(enriched_data)} records)")
