import os
import signal
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from src.config.paths import RAW_DATA_DIR

app = FastAPI(title="Synergy Raw Data API")

# --------------------------------------------------
# Ensure directories exist
# --------------------------------------------------
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

RAW_INMOMENT_FILE = RAW_DATA_DIR / "synergy_inmoment.json"
RAW_FULLSTORY_FILE = RAW_DATA_DIR / "synergy_fullstory.json"

# --------------------------------------------------
# Helper to load JSON
# --------------------------------------------------
def load_json_file(path: Path):
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{path.name} not found")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

# --------------------------------------------------
# Routes for raw data
# --------------------------------------------------
@app.get("/data/raw/synergy_inmoment.json", response_class=JSONResponse)
def get_inmoment_data():
    return load_json_file(RAW_INMOMENT_FILE)

@app.get("/data/raw/synergy_fullstory.json", response_class=JSONResponse)
def get_fullstory_data():
    return load_json_file(RAW_FULLSTORY_FILE)

# --------------------------------------------------
# Kill any process using port 8080 before starting
# --------------------------------------------------
def free_port_8080():
    try:
        # Find PID using port 8080
        result = subprocess.run(
            ["lsof", "-ti", "tcp:8080"], capture_output=True, text=True
        )
        pids = result.stdout.strip().split("\n")
        for pid in pids:
            if pid:
                os.kill(int(pid), signal.SIGTERM)
                print(f"Killed existing process on port 8080: PID {pid}")
    except Exception as e:
        print(f"No existing process on port 8080 or failed to kill: {e}")

# --------------------------------------------------
# Main entry
# --------------------------------------------------
if __name__ == "__main__":
    free_port_8080()
    import uvicorn
    uvicorn.run("data_api:app", host="127.0.0.1", port=8080, reload=True)
