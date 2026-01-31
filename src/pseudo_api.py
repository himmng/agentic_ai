import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / sys.argv[1]
AUG_DIR = PROJECT_ROOT / "data" / "augmented" / sys.argv[2]

def get_surveys():
    return json.loads(RAW_DIR.read_text())

def write_back_augmented(data, overwrite=False):
    if overwrite:
        RAW_DIR.write_text(json.dumps(data, indent=2))
    else:
        AUG_DIR.write_text(json.dumps(data, indent=2))
