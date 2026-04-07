from ingestion.config import GenerationConfig
from ingestion.pipeline import generate_one_inmoment_record


if __name__ == "__main__":
    cfg = GenerationConfig(
        schema_name="inmoment",
        count=1,  # we’ll call it 50 times
        seed=None,
        sink="jsonl",
        output_path="data/inmoment_data.jsonl",
        provider="azure",
    )

    total = 10
    for i in range(total):
        rec = generate_one_inmoment_record(cfg)
        print(f"[{i+1}/{total}] Generated InMoment record: {rec.get('response_id')}")