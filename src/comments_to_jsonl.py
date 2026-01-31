import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

comments = []
with open(DATA_DIR / "random_comments.json", "w", encoding='utf-8') as f:
    json.dump(comments, f, indent=2, ensure_ascii=False)