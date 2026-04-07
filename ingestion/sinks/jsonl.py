import json
from pathlib import Path
from typing import Any, Dict, Iterable


class JsonlSink:
    def __init__(self, path: str | Path):
        self._path = Path(path)

    def write_many(self, records: Iterable[Dict[str, Any]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")