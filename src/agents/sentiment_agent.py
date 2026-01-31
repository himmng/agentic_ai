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
            "You are a sentiment analysis agent for energy utility customer feedback. "
            "Given a customer comment and CSAT score (1–5), classify sentiment strictly as "
            "'positive', 'neutral', or 'negative'. "
            "Use CSAT as a strong prior and comment text as supporting evidence."
        ),
    ),
)

print(
    f"Agent created (id={sentiment_agent.id}, "
    f"name={sentiment_agent.name}, version={sentiment_agent.version})"
)

