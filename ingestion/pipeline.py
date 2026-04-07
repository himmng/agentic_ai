import random
from typing import Dict, Any

from .config import GenerationConfig  # described earlier
from .schemas.registry import load_schema
from .generators.structured import StructuredGenerator
from .llm.inmoment_agent import InMomentTextAgent
from .providers.mock import MockProvider
from .providers.azure import AzureOpenAIProvider
from .validators.pydantic_validator import JsonSchemaValidator
from .sinks.jsonl import JsonlSink


def generate_one_inmoment_record(cfg: GenerationConfig) -> Dict[str, Any]:
    """
    Generate a single InMoment record using structured code + LLM and
    append it to cfg.output_path if sink='jsonl'.

    Returns the generated record.
    """
    if cfg.schema_name != "inmoment":
        raise ValueError("generate_one_inmoment_record: schema_name must be 'inmoment'")

    rng = random.Random(cfg.seed) if cfg.seed is not None else random.Random()
    schema = load_schema("inmoment")

    structured_gen = StructuredGenerator(rng=rng)
    #provider = MockProvider()  # swap to AzureOpenAIProvider when ready
    provider = AzureOpenAIProvider() if cfg.provider == "azure" else MockProvider()
    text_agent = InMomentTextAgent(provider=provider)
    validator = JsonSchemaValidator(schema)

    # 1) Structured generation for entire record
    record: Dict[str, Any] = structured_gen.generate_one(schema)

    # 2) Build LLM context (minimal but sufficient)
    # Ensure customer_id is an int if your prompt expects it
    raw_customer_id = record.get("customer_id")
    try:
        customer_id = int(raw_customer_id) if raw_customer_id is not None else 0
    except (TypeError, ValueError):
        customer_id = 0

    # You can choose complaint_type randomly or derive from somewhere
    complaint_type = rng.choice(["billing", "outage", "pricing", "customer_service", "app"])

    # Build a simplified responses context (only question_id)
    responses_ctx = []
    for resp in record.get("responses") or []:
        qid = resp.get("question_id")
        if qid is not None:
            responses_ctx.append({"question_id": qid})

    context: Dict[str, Any] = {
        "customer_id": customer_id,
        "nps": record.get("nps"),
        "channel": record.get("channel"),
        "complaint_type": complaint_type,
        "complaint_time": record.get("timestamp"),  # or a separate field if you add one
        "responses": responses_ctx,
        "metadata": record.get("metadata", {}),
    }

    # 3) Call LLM agent for comment + answers + tags
    text_result = text_agent.generate(context)

    # 4) Merge LLM output into record
    record["comment"] = text_result.comment
    # Map answers by question_id into the existing responses
    answers_by_qid = {a.get("question_id"): a.get("answer") for a in text_result.answers}
    for resp in record.get("responses") or []:
        qid = resp.get("question_id")
        if qid in answers_by_qid:
            resp["answer"] = answers_by_qid[qid]

    # Optionally add tags if your schema has a tags field or metadata.tag-like structure
    if "tags" in record and isinstance(record["tags"], list):
        record["tags"] = text_result.tags
    elif "metadata" in record and isinstance(record["metadata"], dict):
        record["metadata"]["tags"] = text_result.tags

    # 5) Final validation
    validator.validate(record)

    # 6) Write to sink if desired
    if cfg.sink == "jsonl":
        sink = JsonlSink(cfg.output_path)
        sink.write_many([record])

    return record