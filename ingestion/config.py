from dataclasses import dataclass
from typing import Literal


@dataclass
class GenerationConfig:
    schema_name: Literal["inmoment", "fullstory"]
    count: int = 1
    seed: int | None = None
    sink: Literal["jsonl", "memory"] = "jsonl"
    output_path: str = "data/inmoment_data.jsonl"
    provider: Literal["mock", "azure"] = "mock"