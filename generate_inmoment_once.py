from ingestion.config import GenerationConfig
from ingestion.pipeline import generate_one_inmoment_record


if __name__ == "__main__":
    cfg = GenerationConfig(
        schema_name="inmoment",
        count=1,
        seed=None,
        sink="jsonl",
        output_path="data/inmoment_data.jsonl",
        provider="azure",  # <- switch to Azure
    )
    rec = generate_one_inmoment_record(cfg)
    print("Generated InMoment record:", rec["response_id"])