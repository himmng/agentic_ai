import os
import json
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
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
# Agent environment keys
# --------------------------------------------------
AGENTS = {
    "inmoment": "INMOMENT_DATA_CREATION_AGENT",
    "fullstory": "FULLSTORY_DATA_CREATION_AGENT",
}

# --------------------------------------------------
# Call a single agent (single-sample contract)
# --------------------------------------------------
def call_agent(agent_env_key: str, prompt: dict):
    agent_name = os.getenv(agent_env_key)
    if not agent_name:
        raise ValueError(f"{agent_env_key} not found in environment")

    conversation = openai_client.conversations.create()

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={
            "agent": {
                "name": agent_name,
                "type": "agent_reference",
            }
        },
        input=json.dumps(prompt),
    )

    try:
        data = json.loads(response.output_text.strip())

        # Wrap single object into a list for consistency
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ValueError("Agent output must be a JSON object or array")

        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from agent: {e}")

# --------------------------------------------------
# Orchestrator: ONE correlated sample
# --------------------------------------------------
def orchestrate_single_sample(customer_id: int):
    """
    Generates exactly ONE correlated FullStory + InMoment sample
    """

    inmoment_prompt = {
        "customer_id": customer_id,
        "complaint_type": "billing"
    }

    fullstory_prompt = {
        "customer_id": customer_id,
        "total_sessions": 1,  # single synthetic session per call
        "complaint_trigger": True,
        "complaint_type": "billing"
    }

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            "inmoment": executor.submit(
                call_agent, AGENTS["inmoment"], inmoment_prompt
            ),
            "fullstory": executor.submit(
                call_agent, AGENTS["fullstory"], fullstory_prompt
            )
        }

        inmoment_data = futures["inmoment"].result()
        fullstory_data = futures["fullstory"].result()

    return {
        "customer_id": customer_id,
        "inmoment": inmoment_data,
        "fullstory": fullstory_data
    }

# --------------------------------------------------
# Fan-out / Fan-in: Generate N samples in parallel
# --------------------------------------------------
def generate_n_samples(
    n_samples: int,
    start_customer_id: int = 10001,
    max_workers: int = 10
):
    results = []

    customer_ids = range(
        start_customer_id,
        start_customer_id + n_samples
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(orchestrate_single_sample, cid): cid
            for cid in customer_ids
        }

        for future in as_completed(futures):
            results.append(future.result())

    return results

# --------------------------------------------------
# Persist outputs
# --------------------------------------------------
def save_outputs(results):
    inmoment_all = []
    fullstory_all = []

    for r in results:
        inmoment_all.extend(r["inmoment"])
        fullstory_all.extend(r["fullstory"])

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    inmoment_path = RAW_DATA_DIR / "synergy_inmoment.json"
    fullstory_path = RAW_DATA_DIR / "synergy_fullstory.json"

    inmoment_path.write_text(
        json.dumps(inmoment_all, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    fullstory_path.write_text(
        json.dumps(fullstory_all, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Saved {len(inmoment_all)} InMoment records → {inmoment_path}")
    print(f"Saved {len(fullstory_all)} FullStory records → {fullstory_path}")

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    n = int(input("Enter number of samples to generate: ").strip())
    results = generate_n_samples(n_samples=n)
    save_outputs(results)
