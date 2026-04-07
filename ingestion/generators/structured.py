import uuid
import random
import json
from datetime import datetime, timedelta


# -----------------------------
# BASE UTILITIES
# -----------------------------

def now():
    return datetime.utcnow()


def random_timestamp(start=None):
    start = start or now()
    return (start + timedelta(seconds=random.randint(0, 3600))).isoformat()


def random_id(prefix):
    return f"{prefix}_{random.randint(1, 10000)}"


# -----------------------------
# BASE GENERATOR
# -----------------------------

class BaseDataGenerator:
    def __init__(self, schema):
        self.schema = schema

    def generate(self):
        raise NotImplementedError


# -----------------------------
# INMOMENT GENERATOR
# -----------------------------

class InMomentGenerator(BaseDataGenerator):

    CHANNELS = ["web", "mobile", "email", "in_store"]

    def _generate_nps(self):
        return random.choices(
            population=list(range(11)),
            weights=[1,1,1,1,1,1,2,3,4,5,5]
        )[0]

    def _generate_comment(self, nps):
        if nps <= 6:
            return random.choice([
                "Very poor experience",
                "Support was slow",
                "Not satisfied"
            ])
        elif nps <= 8:
            return random.choice([
                "It was okay",
                "Average experience"
            ])
        else:
            return random.choice([
                "Excellent service",
                "Loved the experience",
                "Very smooth process"
            ])

    def generate(self):
        nps = self._generate_nps()

        return {
            "response_id": str(uuid.uuid4()),
            "timestamp": random_timestamp(),
            "survey_id": random_id("survey"),
            "customer_id": random_id("cust"),
            "channel": random.choice(self.CHANNELS),
            "nps": nps,
            "comment": self._generate_comment(nps),
            "responses": [
                {"question_id": "q1", "answer": nps},
                {"question_id": "q2", "answer": "text"}
            ],
            "metadata": {
                "region": random.choice(["AU", "US", "UK"]),
                "product": random.choice(["A", "B", "C"])
            }
        }


# -----------------------------
# FULLSTORY GENERATOR
# -----------------------------

class FullstoryGenerator(BaseDataGenerator):

    EVENT_TYPES = ["click", "navigate", "scroll", "input", "custom", "error"]
    URLS = ["/home", "/pricing", "/checkout", "/product"]
    DEVICES = ["mobile", "desktop"]
    BROWSERS = ["chrome", "safari", "firefox"]

    def _generate_event_properties(self, event_type):
        if event_type == "click":
            return {"element": "button", "label": "buy"}
        elif event_type == "scroll":
            return {"depth": random.randint(10, 100)}
        elif event_type == "error":
            return {"code": 500, "message": "Server error"}
        return {"info": "generic_event"}

    def generate(self):
        event_type = random.choice(self.EVENT_TYPES)

        return {
            "event_id": str(uuid.uuid4()),
            "timestamp": random_timestamp(),
            "event_type": event_type,
            "user": {
                "user_id": random_id("user"),
                "anonymous_id": str(uuid.uuid4()),
                "properties": {
                    "plan": random.choice(["free", "pro"])
                }
            },
            "session": {
                "session_id": random_id("sess"),
                "device_id": random_id("dev"),
                "view_id": str(uuid.uuid4())
            },
            "page": {
                "url": f"https://example.com{random.choice(self.URLS)}",
                "path": random.choice(self.URLS),
                "referrer": random.choice(["google.com", "direct"])
            },
            "event_properties": self._generate_event_properties(event_type),
            "device": {
                "type": random.choice(self.DEVICES),
                "browser": random.choice(self.BROWSERS),
                "os": random.choice(["ios", "android", "windows"])
            }
        }


# -----------------------------
# FACTORY (KEY COMPONENT)
# -----------------------------

class DataGeneratorFactory:

    @staticmethod
    def create(schema_name, schema):
        if schema_name == "inmoment":
            return InMomentGenerator(schema)
        elif schema_name == "fullstory":
            return FullstoryGenerator(schema)
        else:
            raise ValueError(f"Unknown schema: {schema_name}")


# -----------------------------
# AUGMENTATION LAYER (OPTIONAL)
# -----------------------------

class DataAugmenter:

    def __init__(self, noise=0.1):
        self.noise = noise

    def augment(self, record):
        # Add noise / missing fields
        if random.random() < self.noise:
            if "metadata" in record:
                record["metadata"]["noise_flag"] = True

        return record


# -----------------------------
# MAIN DRIVER
# -----------------------------

def generate_dataset(schema_name, schema, n=1000):
    generator = DataGeneratorFactory.create(schema_name, schema)
    augmenter = DataAugmenter()

    data = []
    for _ in range(n):
        record = generator.generate()
        record = augmenter.augment(record)
        data.append(record)

    return data


# -----------------------------
# WRITE TO JSONL
# -----------------------------

def write_jsonl(data, filename):
    with open(filename, "w") as f:
        for record in data:
            f.write(json.dumps(record) + "\n")


# -----------------------------
# RUN EXAMPLE
# -----------------------------

if __name__ == "__main__":
    inmoment_schema = {}   # placeholder (you already have JSON)
    fullstory_schema = {}

    inmoment_data = generate_dataset("inmoment", inmoment_schema, 100)
    fullstory_data = generate_dataset("fullstory", fullstory_schema, 500)

    write_jsonl(inmoment_data, "inmoment.jsonl")
    write_jsonl(fullstory_data, "fullstory.jsonl")