import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from pathlib import Path
import json

# --------------------------------------------------
# Project and data paths
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[0]
print("PROJECT_ROOT:", PROJECT_ROOT)
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
print("DATA_DIR:", DATA_DIR)
# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv(PROJECT_ROOT / "agents" / ".env")

# --------------------------------------------------
# Initialize Azure AI Project client
# --------------------------------------------------
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
if not PROJECT_ENDPOINT:
    raise ValueError("PROJECT_ENDPOINT not set in .env")

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

# --------------------------------------------------
# Select agent dynamically
# --------------------------------------------------
AGENT_KEY = "DATA_CREATION_AGENT"  # Example: hardcoded for testing

if AGENT_KEY not in os.environ:
    raise ValueError(f"{AGENT_KEY} not found in .env")

AGENT_NAME = os.environ[AGENT_KEY]
print(f"Using agent: {AGENT_NAME}")

# --------------------------------------------------
# Get user prompt
# --------------------------------------------------
USER_PROMPT = input("\nEnter the prompt to send to the agent:\n").strip()
if not USER_PROMPT:
    raise ValueError("Prompt cannot be empty")

# --------------------------------------------------
# Create conversation
# --------------------------------------------------
conversation = openai_client.conversations.create()
print(f"\nConversation ID: {conversation.id}")

# --------------------------------------------------
# Invoke agent
# --------------------------------------------------
try:
    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={
            "agent": {
                "name": AGENT_NAME,
                "type": "agent_reference"
            }
        },
        input=USER_PROMPT
    )

    print("\n===== AGENT OUTPUT =====")
    
    # -----------------------------
    # Special handling for DATA_CREATION_AGENT
    # -----------------------------
    if AGENT_KEY == "DATA_CREATION_AGENT":
        output_file = DATA_DIR / "synergy_inmoment.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Load new data from agent
        try:
            new_data = json.loads(response.output_text)
            if not isinstance(new_data, list):
                raise ValueError("Agent output must be a JSON array!")
        except json.JSONDecodeError as e:
            print("Error parsing agent output:", e)
            new_data = []

        # Load existing data if file exists
        if output_file.exists():
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        raise ValueError("Existing JSON file is not an array!")
            except json.JSONDecodeError:
                existing_data = []
        else:
            existing_data = []

        # Append new objects
        combined_data = existing_data + new_data

        # Write combined array back to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)

        print(f"\nAppended {len(new_data)} new objects. Total now: {len(combined_data)}")
        print(f"Data saved to: {output_file}")

    # -----------------------------
    # Other agents: just print output
    # -----------------------------
    else:
        print(response.output_text)

except Exception as e:
    print("\nError running agent:", e)
