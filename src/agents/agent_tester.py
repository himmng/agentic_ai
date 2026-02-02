# agent_tester.py
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from pathlib import Path
#---------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

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
# Select agent dynamically (same style as agent_creator)
# --------------------------------------------------
AGENT_KEY = input("Provide AGENT_KEY (e.g. DATA_CREATION_AGENT): ").strip().upper()

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
# Create conversation (recommended)
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
    print(response.output_text)

except Exception as e:
    print("\nError running agent:", e)
