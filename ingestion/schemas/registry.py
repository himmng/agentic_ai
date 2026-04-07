from pathlib import Path
from typing import Any, Dict

import yaml

_BASE_PATH = Path(__file__).parent / "definitions"
_CACHE: dict[str, Dict[str, Any]] = {}


def load_schema(name: str) -> Dict[str, Any]:
    """
    Load a JSON Schema-like dict from definitions/<name>.yaml.
    """
    if name in _CACHE:
        return _CACHE[name]

    path = _BASE_PATH / f"{name}.yaml"
    if not path.exists():
        raise ValueError(f"Schema {name!r} not found at {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Schema root must be a JSON object")
    _CACHE[name] = data
    return data