import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

# Create project client
project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# ---- Create sentiment agent ONCE ----
sentiment_agent = project_client.agents.create_version(
    agent_name=os.environ["SENTIMENT_AGENT_NAME"],
    definition=PromptAgentDefinition(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        instructions=(
            "You are a Data Retrieval Agent for Synergy WA customer surveys (InMoment API format). Your task:"
    "1. Fetch survey responses from the InMoment API (assume the Python code handles the actual API call)."
    2. Only retain these fields for downstream agents: "score", "text", "tags".
    3. Ensure all survey responses are complete (completed=True) and not excluded from calculations (excluded_from_calculations=False).
    4. Return the results as a JSON array of objects with the specified fields.
    5. Stop fetching if the parameter stopping=True is passed.
"
        ),
    ),
)

print(
    f"Agent created (id={sentiment_agent.id}, "
    f"name={sentiment_agent.name}, version={sentiment_agent.version})"
)

