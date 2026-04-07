import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from .config import GenerationConfig
from .schemas.registry import load_schema
from .generators.structured import StructuredGenerator
from .llm.inmoment_agent import InMomentTextAgent
from .providers.mock import MockProvider
from .providers.azure import AzureOpenAIProvider
from .validators.pydantic_validator import JsonSchemaValidator
from .sinks.jsonl import JsonlSink
from .id_state import load_id_state, save_id_state, IdState


def generate_one_inmoment_record(cfg: GenerationConfig) -> Dict[str, Any]:
    """
    Generate a single InMoment record using structured code + LLM, with
    stable, non-repeating IDs across runs (via ID state).
    """
    if cfg.schema_name != "inmoment":
        raise ValueError("generate_one_inmoment_record: schema_name must be 'inmoment'")

    rng = random.Random(cfg.seed) if cfg.seed is not None else random.Random()

    # 0) Load current ID state
    state: IdState = load_id_state("inmoment")

    schema = load_schema("inmoment")
    structured_gen = StructuredGenerator(rng=rng)

    provider = AzureOpenAIProvider() if cfg.provider == "azure" else MockProvider()
    text_agent = InMomentTextAgent(provider=provider)
    validator = JsonSchemaValidator(schema)

    # 1) Structured generation for entire record
    record: Dict[str, Any] = structured_gen.generate_one(schema)

    # 1a) Customer ID pattern: CUST000, CUST001, ...
    customer_id_pattern = "CUST{index:03d}"
    record["customer_id"] = customer_id_pattern.format(index=state.customer_next_index)
    state.customer_next_index += 1

    # 1b) Survey ID pattern: SUR000, SUR001, ...
    survey_id_pattern = "SUR{index:03d}"
    record["survey_id"] = survey_id_pattern.format(index=state.survey_next_index)
    # Option: either reuse a small set or advance each time; here we advance
    state.survey_next_index += 1

    # 1c) Response ID pattern: RSP0000000, RSP0000001, ...
    response_id_pattern = "RSP{index:07d}"
    record["response_id"] = response_id_pattern.format(index=state.response_next_index)
    state.response_next_index += 1

    # 1d) Realistic timestamp within a recent window (last 30 days)
    now = datetime.now(timezone.utc)
    days_back = rng.randint(0, 29)
    seconds_in_day = rng.randint(0, 24 * 3600 - 1)
    ts = now - timedelta(days=days_back, seconds=seconds_in_day)
    record["timestamp"] = ts.isoformat().replace("+00:00", "Z")

    # 1e) More realistic channel distribution
    channels = [
        ("web", 0.5),
        ("mobile", 0.3),
        ("email", 0.15),
        ("in_store", 0.05),
    ]
    r_channel = rng.random()
    cum = 0.0
    chosen_channel = "web"
    for name, weight in channels:
        cum += weight
        if r_channel <= cum:
            chosen_channel = name
            break
    record["channel"] = chosen_channel

    # 2) Build LLM context
    try:
        customer_id_int = int(state.customer_next_index - 1)  # or parse from string if your prompt truly needs int
    except (TypeError, ValueError):
        customer_id_int = 0

    complaint_type = rng.choice(["billing", "outage", "pricing", "customer_service", "app"])

    responses_ctx = []
    for resp in record.get("responses") or []:
        qid = resp.get("question_id")
        if qid is not None:
            responses_ctx.append({"question_id": qid})

    context: Dict[str, Any] = {
        "customer_id": customer_id_int,
        "nps": record.get("nps"),
        "channel": record.get("channel"),
        "complaint_type": complaint_type,
        "complaint_time": record.get("timestamp"),
        "responses": responses_ctx,
        "metadata": record.get("metadata", {}),
    }

    # 3) Call LLM agent for comment + answers + tags
    text_result = text_agent.generate(context)

    # 4) Merge LLM output into record
    record["comment"] = text_result.comment

    answers_by_qid = {a.get("question_id"): a.get("answer") for a in text_result.answers}
    for resp in record.get("responses") or []:
        qid = resp.get("question_id")
        if qid in answers_by_qid:
            resp["answer"] = answers_by_qid[qid]

    if "tags" in record and isinstance(record["tags"], list):
        record["tags"] = text_result.tags
    elif "metadata" in record and isinstance(record["metadata"], dict):
        record["metadata"]["tags"] = text_result.tags

    # 5) Final validation
    validator.validate(record)

    # 6) Persist updated ID state
    save_id_state("inmoment", state)

    # 7) Write to sink if desired
    if cfg.sink == "jsonl":
        sink = JsonlSink(cfg.output_path)
        sink.write_many([record])

    return record