import random
import string
from typing import Any, Dict

from .base import BaseGenerator


class StructuredGenerator(BaseGenerator):
    """
    Generic JSON-Schema-ish generator using Python's random.

    For InMoment, this will produce a full record with:
      - IDs, timestamps, enums, numeric values
      - responses[].question_id
    The LLM will overwrite text fields (e.g. comment, responses[].answer).
    """

    def __init__(self, rng: random.Random | None = None):
        self._rng = rng or random.Random()

    def generate_one(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        if schema.get("type") != "object":
            raise ValueError("Top-level schema must be an object")
        return self._gen_object(schema)

    # --- internal helpers ---

    def _gen_object(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        props: Dict[str, Any] = schema.get("properties", {})
        out: Dict[str, Any] = {}
        for name, subschema in props.items():
            out[name] = self._gen_value(subschema)
        return out

    def _gen_value(self, schema: Dict[str, Any]) -> Any:
        if "enum" in schema:
            return self._rng.choice(schema["enum"])

        t = schema.get("type")
        if t == "string":
            fmt = schema.get("format")
            if fmt == "date-time":
                # You can replace this with realistic date ranges if needed
                return "2024-01-01T00:00:00Z"
            return self._random_string(12)

        if t == "integer":
            lo = schema.get("minimum", 0)
            hi = schema.get("maximum", lo + 100)
            return self._rng.randint(lo, hi)

        if t == "number":
            lo = schema.get("minimum", 0)
            hi = schema.get("maximum", lo + 100.0)
            return self._rng.uniform(lo, hi)

        if t == "object":
            return self._gen_object(schema)

        if t == "array":
            items = schema.get("items", {})
            length = self._rng.randint(1, 3)
            return [self._gen_value(items) for _ in range(length)]

        # Fallback
        return None

    def _random_string(self, n: int) -> str:
        chars = string.ascii_letters + string.digits
        return "".join(self._rng.choice(chars) for _ in range(n))