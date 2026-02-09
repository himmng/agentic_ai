import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from src.config.paths import ENV, RAW_DATA_DIR
from concurrent.futures import ThreadPoolExecutor

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
# Agent environment keys
# --------------------------------------------------
AGENTS = {
    "inmoment": ("INMOMENT_DATA_CREATION_AGENT", "synergy_inmoment.json"),
    "fullstory": ("FULLSTORY_DATA_CREATION_AGENT", "synergy_fullstory.json"),
}

# --------------------------------------------------
# Function to call a single agent
# --------------------------------------------------
def call_agent(agent_env_key, prompt):
    agent_name = os.environ.get(agent_env_key)
    if not agent_name:
        raise ValueError(f"{agent_env_key} not found in .env")

    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
        input=prompt,
    )

    try:
        data = json.loads(response.output_text)
        if not isinstance(data, list):
            raise ValueError("Agent output must be a JSON array!")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing agent output: {e}")

# --------------------------------------------------
# Orchestrator function
# --------------------------------------------------
def orchestrate_generation(n_samples):
    """
    Orchestrates generating synthetic data for both agents with shared customer_ids
    """

    # Generate shared customer IDs
    customer_ids = list(range(10001, 10001 + n_samples))

    # Build prompts with customer_id info for correlation
    inmoment_prompt = f"Generate {n_samples} InMoment survey responses with customer_ids: {customer_ids}"
    fullstory_prompt = f"Generate {n_samples} FullStory session records with customer_ids: {customer_ids}. Include some random sessions not linked to survey."

    # Run agents concurrently
    with ThreadPoolExecutor() as executor:
        future_inmoment = executor.submit(call_agent, AGENTS["inmoment"][0], inmoment_prompt)
        future_fullstory = executor.submit(call_agent, AGENTS["fullstory"][0], fullstory_prompt)

        inmoment_data = future_inmoment.result()
        fullstory_data = future_fullstory.result()

    # Save outputs
    inmoment_file = RAW_DATA_DIR / AGENTS["inmoment"][1]
    fullstory_file = RAW_DATA_DIR / AGENTS["fullstory"][1]
    inmoment_file.parent.mkdir(parents=True, exist_ok=True)

    for file_path, data in [(inmoment_file, inmoment_data), (fullstory_file, fullstory_data)]:
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
        else:
            existing_data = []

        combined_data = existing_data + data
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(data)} new objects to {file_path}. Total now: {len(combined_data)}")

    return {"inmoment": inmoment_data, "fullstory": fullstory_data}

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    n_samples = int(input("Enter number of samples to generate: ").strip())
    orchestrate_generation(n_samples)
