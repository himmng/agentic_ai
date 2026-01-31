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

AGENT_NAME = os.environ[input("Provide the name for the agent: ").strip().upper()]
PROMPT_PATH = os.environ["PROMPT_PATH"] + AGENT_NAME + "-prompt.txt"

if not PROMPT_PATH:
    raise ValueError("PROMPT_PATH not set in .env")

def load_prompt():
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()
    
# agent creation
print(f"Trying to create Agent: {AGENT_NAME}")
prompt = load_prompt()
print("Loaded Prompt:")
print(prompt)


##---- Create sentiment agent ONCE ----
sentiment_agent = project_client.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        instructions=prompt,
    ),
)

print(
    f"Agent created (id={sentiment_agent.id}, "
    f"name={sentiment_agent.name}, version={sentiment_agent.version})"
)
