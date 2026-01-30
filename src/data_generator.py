import random
import json
from faker import Faker
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "augmented"

fake = Faker("en_AU")

import random
from datetime import datetime, timezone
from faker import Faker

fake = Faker()

def generate_survey(i, comments, seed=None):
    if seed is not None:
        random.seed(seed + i)

    csat = random.randint(1, 5)
    ces = random.randint(1, 7)

    priority = (
        "HIGH" if ces <= 3 else
        "MEDIUM" if ces <= 5 else
        "LOW"
    )

    escalation = ces <= 3

    now = datetime.now(timezone.utc).isoformat()

    return {
        # ---- Core response identity ----
        "id": i,
        "uuid": f"WA-RESP-{i:06d}",
        "surveyId": 2026,
        "surveyName": "Synergy WA Digital CX Survey",

        # ---- Status ----
        "complete": True,
        "exclusionReason": "NONE",

        # ---- Timing ----
        "beginTime": now,
        "lastModTime": now,
        "dateOfService": now,

        # ---- Network / origin ----
        "ipAddress": fake.ipv4_public(),
        "url": "https://www.synergy.net.au/my-account",

        # ---- Answers (free-text + structured) ----
        "answers": [
            {
                "fieldId": 101,
                "fieldName": "CES",
                "fieldType": "scale",
                "literalValue": str(ces)
            },
            {
                "fieldId": 102,
                "fieldName": "CSAT",
                "fieldType": "scale",
                "literalValue": str(csat)
            },
            {
                "fieldId": 103,
                "fieldName": "Customer Comment",
                "fieldType": "text",
                "literalValue": random.choice(comments)
            }
        ],

        # ---- Scores (InMoment-native analytics) ----
        "scores": [
            {
                "fieldId": 101,
                "fieldName": "CES",
                "score": ces,
                "points": ces,
                "pointsPossible": 7
            },
            {
                "fieldId": 102,
                "fieldName": "CSAT",
                "score": csat,
                "points": csat,
                "pointsPossible": 5
            }
        ],

        # ---- Tags (used for AI + dashboards + routing) ----
        "tags": [
            {
                "name": f"PRIORITY_{priority}",
                "label": f"Priority {priority}",
                "enabled": True,
                "visibleInInbox": True
            },
            {
                "name": "DIGITAL_CHANNEL",
                "label": "Website / My Account",
                "enabled": True,
                "visibleInInbox": False
            }
        ],

        # ---- Incidents (InMoment escalation model) ----
        "incidents": (
            [{
                "dateTimeUTC": now,
                "incidentManagementState": "OPEN",
                "comment": "Low CES score triggered automated escalation"
            }] if escalation else []
        ),

        # ---- End user snapshot ----
        "contact": {
            "id": f"CUST-{i:06d}",
            "organizationId": 999,
            "email": fake.email(),
            "phone": fake.phone_number(),
            "fields": [
                {"fieldId": 201, "value": "WA"},
                {"fieldId": 202, "value": "Residential"},
                {"fieldId": 203, "value": "Electricity"}
            ]
        }
    }

if __name__ == "__main__":
    with open(DATA_DIR / "random_comments.json") as f:
        comments = json.load(f)
    surveys = [generate_survey(i, comments) for i in range(len(comments))]
    with open(DATA_DIR / "inmoment_surveys.json", "w") as f:
        json.dump(surveys, f, indent=2)
