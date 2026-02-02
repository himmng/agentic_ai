import os
from dotenv import load_dotenv
import json
import requests
from pathlib import Path
from typing import List, Dict

# -----------------------------
# Project and data paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[0]
RAW_FILE = Path(__file__).resolve().parents[1] / "data" / "raw" / "synergy_inmoment.json"
EXTRACTED_FILE = Path(__file__).resolve().parents[1] / "data" / "extracted" / "synergy_inmoment_extracted.json"
PROCESSED_FILE = Path(__file__).resolve().parents[1] / "data" / "processed" / "synergy_inmoment_processed.json"
PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Config
# -----------------------------
load_dotenv(PROJECT_ROOT / "agents" / ".env")
LOCAL_API_RAW_URL = "http://127.0.0.1:8080/synergy_inmoment.json"
LOCAL_API_EXTRACTED_URL = "http://127.0.0.1:8080/synergy_inmoment_extracted.json"

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
# Fetch JSON data from API or fallback to file
# -----------------------------
def fetch_json(source: str) -> List[Dict]:
    if source == "raw":
        url = LOCAL_API_RAW_URL
        file_path = RAW_FILE
    elif source == "extracted":
        url = LOCAL_API_EXTRACTED_URL
        file_path = EXTRACTED_FILE
    else:
        file_path = PROCESSED_FILE
        if not file_path.exists():
            print(f"Processed file not found: {file_path}")
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Fetch from API if exists
    try:
        print(f"Fetching data from API: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API fetch failed ({e}), falling back to file: {file_path}")
        if not file_path.exists():
            print("File not found!")
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

# -----------------------------
# Extract relevant fields (only for raw)
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
            "score": s.get("scores")[0]["score"] or s.get("scores")[0]["value"] if s.get("scores") else None,
            "text": s.get("answers")[0]["text"] if s.get("answers") else "",
            "tags": [t["tag"] for t in s.get("tags", []) if t.get("tag")],
        }
        extracted.append(survey_obj)
    return extracted

# -----------------------------
# Incremental load with AI enrichment
# -----------------------------
def incremental_load_with_ai(openai_client, AGENT_NAME, conversation_id, source="raw"):
    seen_ids = load_seen_ids()
    data = fetch_json(source)
    
    if source == "raw":
        data = extract_relevant_fields(data)

    # Filter only new surveys
    new_surveys = [s for s in data if s["id"] not in seen_ids]

    if not new_surveys:
        print("No new survey responses to enrich.")
        return

    agent_input = json.dumps(new_surveys, ensure_ascii=False)

    # Call AI agent
    response = openai_client.responses.create(
        conversation=conversation_id,
        extra_body={
            "agent": {"name": AGENT_NAME, "type": "agent_reference"}
        },
        input=agent_input
    )

    enriched_json_text = response.output_text.strip()

    # Parse enriched data
    try:
        enriched_data = json.loads(enriched_json_text)
    except json.JSONDecodeError as e:
        print("AI output is not valid JSON:", e)
        return

    # Append enriched surveys to processed file
    if PROCESSED_FILE.exists():
        with open(PROCESSED_FILE, "r+", encoding="utf-8") as f:
            processed_data = json.load(f)
            processed_data.extend(enriched_data)
            f.seek(0)
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
            f.truncate()
    else:
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            json.dump(enriched_data, f, indent=2, ensure_ascii=False)

    print(f"Processed and enriched {len(enriched_data)} new survey responses. Total saved: {len(enriched_data) + len(seen_ids)}")

# -----------------------------
# Run manually
# -----------------------------
if __name__ == "__main__":
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    import os

    PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
    if not PROJECT_ENDPOINT:
        raise ValueError("PROJECT_ENDPOINT not set in .env")

    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    openai_client = project_client.get_openai_client()

    AGENT_NAME = os.environ.get("SURVEY_INTELLIGENCE_AGENT")
    if not AGENT_NAME:
        raise ValueError("SURVEY_INTELLIGENCE_AGENT not found in .env")

    conversation = openai_client.conversations.create()

    # Choose source: raw / extracted / processed
    SOURCE = "raw"
    incremental_load_with_ai(openai_client, AGENT_NAME, conversation.id, source=SOURCE)
