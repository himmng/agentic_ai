import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from src.config.paths import ENV

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv(ENV)

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
if not PROJECT_ENDPOINT:
    raise ValueError("PROJECT_ENDPOINT not set in .env")

# --------------------------------------------------
# Initialize Azure AI Project client
# --------------------------------------------------
project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)
openai_client = project_client.get_openai_client()

# --------------------------------------------------
# Agent interaction
# --------------------------------------------------
def main():
    AGENT_KEY = input("Provide AGENT_KEY (e.g., DATA_CREATION_AGENT): ").strip().upper()

    if AGENT_KEY not in os.environ:
        raise ValueError(f"{AGENT_KEY} not found in .env")

    AGENT_NAME = os.environ[AGENT_KEY]
    print(f"Using agent: {AGENT_NAME}")

    USER_PROMPT = input("\nEnter the prompt to send to the agent:\n").strip()
    if not USER_PROMPT:
        raise ValueError("Prompt cannot be empty")

    # Create conversation
    conversation = openai_client.conversations.create()
    print(f"\nConversation ID: {conversation.id}")

    # Invoke agent
    try:
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent": {"name": AGENT_NAME, "type": "agent_reference"}
            },
            input=USER_PROMPT,
        )

        print("\n===== AGENT OUTPUT =====")
        print(response.output_text)

    except Exception as e:
        print("\nError running agent:", e)
        raise

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    main()
