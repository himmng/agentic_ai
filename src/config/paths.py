from pathlib import Path
import os

#-----------------
# project paths
#-----------------

## Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

## Data directory

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
EXTRACTED_DATA_DIR = DATA_DIR / "extracted"
ENRICHED_DATA_DIR = DATA_DIR / "enriched"


## sources directory

SRC_DIR = PROJECT_ROOT / "src"
AGENTS_DIR = SRC_DIR / "agents"
AGENT_PROMPTS_DIR = AGENTS_DIR / ".prompts"
EXTRACTORS_DIR = SRC_DIR / "extractors"


## Notebooks directory

NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

## ENV configuration file

ENV = PROJECT_ROOT / ".env"