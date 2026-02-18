import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from src.config.paths import ENV, AGENT_PROMPTS_DIR

# --------------------------------------------------
# Load environment
# --------------------------------------------------
load_dotenv(ENV)

PROJECT_ENDPOINT = os.environ["PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT_NAME = os.environ["MODEL_DEPLOYMENT_NAME"]

# Ensure prompt directory exists
AGENT_PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Azure Project client
# --------------------------------------------------
project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

# --------------------------------------------------
# Agent name input
# --------------------------------------------------
AGENT_KEY = input("Provide the name for the agent: ").strip().upper()

def to_agent_name(agent_key: str) -> str:
    """Convert ENV key to kebab-case agent name"""
    return agent_key.lower().replace("_", "-")

# --------------------------------------------------
# New agent bootstrap
# --------------------------------------------------
if AGENT_KEY not in os.environ:
    AGENT_NAME = to_agent_name(AGENT_KEY)
    PROMPT_FILE = f"{AGENT_NAME}-prompt.txt"
    PROMPT_PATH = AGENT_PROMPTS_DIR / PROMPT_FILE

    # 1. Append agent key to .env
    with ENV.open("a", encoding="utf-8") as env:
        env.write(f"\n{AGENT_KEY}={AGENT_NAME}\n")

    # 2. Create blank prompt file
    with PROMPT_PATH.open("w", encoding="utf-8") as f:
        f.write(
            "### Instructions\n"
            "Describe the agent's role, inputs, outputs, and constraints here.\n"
        )

    print(" New agent registered")
    print(f"   AGENT KEY     : {AGENT_KEY}")
    print(f"   AGENT NAME  : {AGENT_NAME}")
    print(f"   PROMPT FILE : {PROMPT_PATH}")
    print("\n Edit the prompt file, then rerun this script to create the agent.")
    exit(0)

# --------------------------------------------------
# Existing agent update
# --------------------------------------------------
AGENT_NAME = os.environ[AGENT_KEY]
PROMPT_PATH = AGENT_PROMPTS_DIR / f"{AGENT_NAME}-prompt.txt"

if not PROMPT_PATH.exists():
    raise FileNotFoundError(f"Prompt file missing: {PROMPT_PATH}")

def load_prompt() -> str:
    with PROMPT_PATH.open("r", encoding="utf-8") as f:
        return f.read().strip()

prompt = load_prompt()
if not prompt:
    raise ValueError("Prompt file is empty. Fill it before creating agent.")

print(f"Creating new version for agent: {AGENT_NAME}")

# --------------------------------------------------
# Create agent version
# --------------------------------------------------
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
