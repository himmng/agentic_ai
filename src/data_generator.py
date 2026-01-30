import random
import json
from faker import Faker
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "augmented"

fake = Faker("en_AU")

def generate_survey(i, comments=[]):
    csat = random.randint(1, 5)
    ces = random.randint(1, 7)
    return {
        "response_id": f"WA-R-{i:04d}",
        "survey_id": "SYNERGY-WA-2026",
        "region": "WA",
        "submitted_at": fake.iso8601(),
        "answers": {
            "csat": csat,
            "ces": ces,
            "comment": random.choice(comments)
        },
        "tags": [],
        "case": {
            "priority": "normal",
            "incident": False,
            "notes": []
        },
        "workflow": {
            "assigned_team": None,
            "sla_hours": None,
            "escalation": False
        }
    }

if __name__ == "__main__":
    with open(DATA_DIR / "random_comments.json") as f:
        comments = json.load(f)
    surveys = [generate_survey(i, comments) for i in range(len(comments))]
    with open(DATA_DIR / "inmoment_surveys.json", "w") as f:
        json.dump(surveys, f, indent=2)
