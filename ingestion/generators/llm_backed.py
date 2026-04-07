from typing import Any, Dict, List

from .base import BaseGenerator
from ..providers.base import BaseProvider


class LLMBackedGenerator(BaseGenerator):
    """
    LLM-based enrichment of records.

    Intended usage in the pipeline:
      1) record = structured_gen.generate_one(schema)
      2) record = llm_gen.enrich_record(record, schema)
    """

    def __init__(self, provider: BaseProvider):
        self._provider = provider

    def generate_one(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        # We treat this class as an enricher, so we don't implement this.
        raise NotImplementedError("Use enrich_record(record, schema) instead")

    def enrich_record(self, record: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mutate and return the record, filling free-text fields via LLM.

        Currently:
          - InMoment: 'comment' (string) and 'responses[].answer'
          - Fullstory: no-op (no explicit text feedback fields yet)
        """
        props: Dict[str, Any] = schema.get("properties", {})

        # InMoment 'comment'
        if "comment" in props and props["comment"].get("type") == "string":
            prompt = self._build_comment_prompt(record)
            record["comment"] = self._provider.generate_text(prompt)

        # InMoment 'responses[].answer'
        if "responses" in props and props["responses"].get("type") == "array":
            items_schema = props["responses"].get("items", {})
            if items_schema.get("type") == "object":
                for resp in record.get("responses", []):
                    if "answer" in items_schema.get("properties", {}):
                        prompt = self._build_answer_prompt(record, resp)
                        resp["answer"] = self._provider.generate_text(prompt)

        return record

    # --- prompt builders ---

    def _build_comment_prompt(self, record: Dict[str, Any]) -> str:
        nps = record.get("nps")
        channel = record.get("channel")
        return (
            "You are generating synthetic customer feedback for an NPS survey. "
            f"The NPS score is {nps} and the channel is '{channel}'. "
            "Write 1–3 natural sentences that a real customer might write."
        )

    def _build_answer_prompt(self, record: Dict[str, Any], response: Dict[str, Any]) -> str:
        qid = response.get("question_id")
        nps = record.get("nps")
        return (
            "You are generating synthetic survey answers. "
            f"Question ID: {qid}. NPS score: {nps}. "
            "Write a short, natural-sounding answer (1–2 sentences)."
        )