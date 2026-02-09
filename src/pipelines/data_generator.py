import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from src.config.paths import ENV, RAW_DATA_DIR

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv(ENV)

# --------------------------------------------------
# Initialize Azure AI Project client
# --------------------------------------------------
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
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
def select_agent():
    choice = input(
        "Choose agent:\n"
        "1: inmoment data creation agent\n"
        "2: fullstory data creation agent\n"
        "Selection: "
    ).strip()

    if choice == "1":
        return "INMOMENT_DATA_CREATION_AGENT", "synergy_inmoment.json"
    elif choice == "2":
        return "FULLSTORY_DATA_CREATION_AGENT", "synergy_fullstory.json"
    else:
        raise ValueError("Invalid selection")

# --------------------------------------------------
# Main logic
# --------------------------------------------------
def main():
    AGENT_KEY, savefilename = select_agent()

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

    try:
        response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent": {"name": AGENT_NAME, "type": "agent_reference"}
            },
            input=USER_PROMPT,
        )

        print("\n===== AGENT OUTPUT =====")

        # Prepare output file
        output_file = RAW_DATA_DIR / savefilename
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Load new data
        try:
            new_data = json.loads(response.output_text)
            if not isinstance(new_data, list):
                raise ValueError("Agent output must be a JSON array!")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing agent output: {e}")

        # Load existing data if file exists
        if output_file.exists():
            try:
                with output_file.open("r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        raise ValueError("Existing JSON file is not an array!")
            except json.JSONDecodeError:
                existing_data = []
        else:
            existing_data = []

        # Append and save
        combined_data = existing_data + new_data
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)

        print(f"\nAppended {len(new_data)} new objects. Total now: {len(combined_data)}")
        print(f"Data saved to: {output_file}")

    except Exception as e:
        print("\nError running agent:", e)
        raise

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    main()
