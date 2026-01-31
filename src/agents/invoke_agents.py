# invoke_agents.py
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

# --- Initialize Azure AI Project client ---
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
if not PROJECT_ENDPOINT:
    raise ValueError("PROJECT_ENDPOINT not set in environment variables")

project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential()
)

# --- Main helper: run sentiment agent ---
def sentiment_agent_run(comment: str, csat: int, agent_name: str = None) -> str:
    """
    Run sentiment agent on a comment and CSAT score.
    Uses the new Azure AI Projects SDK pattern (OpenAI client + agent_reference).
    """
    if agent_name is None:
        agent_name = os.environ.get("SENTIMENT_AGENT_NAME")
        if not agent_name:
            raise ValueError("SENTIMENT_AGENT_NAME not set in environment")

    # Get OpenAI client
    openai_client = project_client.get_openai_client()

    # Create a conversation for context (optional, supports multi-turn)
    conversation = openai_client.conversations.create()

    # Mask comment (optional)
    masked_comment = " ".join("*" * len(w) for w in comment.split())

    # Build prompt
    prompt = f"Comment: {masked_comment}\nCSAT: {csat}\nClassify sentiment strictly as 'positive', 'neutral', or 'negative'."

    # Run agent
    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
        input=prompt
    )

    return response.output_text.strip().lower()
