from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from src.config.paths import RAW_DATA_DIR, EXTRACTED_DATA_DIR

app = FastAPI(title="Synergy Data API")

# --------------------------------------------------
# Ensure directories exist
# --------------------------------------------------
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DATA_DIR.mkdir(parents=True, exist_ok=True)

EXTRACTED_FILE = EXTRACTED_DATA_DIR / "synergy_extracted.jsonl"
RAW_FILE = RAW_DATA_DIR / "synergy_raw.jsonl"

# --------------------------------------------------
# Routes
# --------------------------------------------------
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
