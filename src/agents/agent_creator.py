import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# ----------------------------
# Load environment
# ----------------------------
load_dotenv()

PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT_NAME = os.environ["MODEL_DEPLOYMENT_NAME"]
PROMPT_BASE_PATH = os.environ.get("PROMPT_PATH", ".prompts/")

os.makedirs(PROMPT_BASE_PATH, exist_ok=True)

# ----------------------------
# Azure Project client
# ----------------------------
project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

# ----------------------------
# Agent name handling
# ----------------------------
AGENT_KEY = input("Provide the name for the agent: ").strip().upper()
ENV_FILE = ".env"

def to_agent_name(agent_key: str) -> str:
    """Convert ENV key to kebab-case agent name"""
    return agent_key.lower().replace("_", "-")

# ----------------------------
# New agent bootstrap
# ----------------------------
if AGENT_KEY not in os.environ:
    AGENT_NAME = to_agent_name(AGENT_KEY)
    PROMPT_FILE = f"{AGENT_NAME}-prompt.txt"
    PROMPT_PATH = os.path.join(PROMPT_BASE_PATH, PROMPT_FILE)

    # 1. Append agent key to .env
    with open(ENV_FILE, "a", encoding="utf-8") as env:
        env.write(f"\n{AGENT_KEY}={AGENT_NAME}\n")

    # 2. Create blank prompt file
    with open(PROMPT_PATH, "w", encoding="utf-8") as f:
        f.write(
            "### Instructions\n"
            "Describe the agent's role, inputs, outputs, and constraints here.\n"
        )

    print(" New agent registered")
    print(f"   ENV KEY     : {AGENT_KEY}")
    print(f"   AGENT NAME  : {AGENT_NAME}")
    print(f"   PROMPT FILE : {PROMPT_PATH}")
    print("\n Edit the prompt file, then rerun this script to create the agent.")
    exit(0)

# ----------------------------
# Existing agent update
# ----------------------------
AGENT_NAME = os.environ[AGENT_KEY]
PROMPT_PATH = os.path.join(PROMPT_BASE_PATH, f"{AGENT_NAME}-prompt.txt")

if not os.path.exists(PROMPT_PATH):
    raise FileNotFoundError(f"Prompt file missing: {PROMPT_PATH}")

def load_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()

prompt = load_prompt()

if not prompt:
    raise ValueError("Prompt file is empty. Fill it before creating agent.")

print(f"Creating new version for agent: {AGENT_NAME}")

# ----------------------------
# Create agent version
# ----------------------------
agent = project_client.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT_NAME,
        instructions=prompt,
    ),
)

print(
    f"  Agent version created\n"
    f"   ID      : {agent.id}\n"
    f"   Name    : {agent.name}\n"
    f"   Version : {agent.version}"
)
