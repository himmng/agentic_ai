from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pathlib import Path

app = FastAPI(title="Synergy Data API")

# Resolve project root (agentic_ai)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

EXTRACTED_FILE = DATA_DIR / "extracted" / "synergy_extracted.jsonl"
RAW_FILE = DATA_DIR / "raw" / "synergy_raw.jsonl"

@app.get("/data/extracted/synergy_extracted.jsonl", response_class=PlainTextResponse)
def get_extracted_data():
    if not EXTRACTED_FILE.exists():
        raise HTTPException(status_code=404, detail="Extracted data not found")
    return EXTRACTED_FILE.read_text(encoding="utf-8")

@app.get("/data/raw/synergy_raw.jsonl", response_class=PlainTextResponse)
def get_raw_data():
    if not RAW_FILE.exists():
        raise HTTPException(status_code=404, detail="Raw data not found")
    return RAW_FILE.read_text(encoding="utf-8")
