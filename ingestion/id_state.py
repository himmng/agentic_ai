from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal


SchemaName = Literal["inmoment", "fullstory"]  # extend as needed


@dataclass
class IdState:
    customer_next_index: int = 0      # next index for customer_id pattern
    survey_next_index: int = 0        # next index for survey_id pattern (if you want)
    response_next_index: int = 0      # next index for response_id pattern


_STATE_DIR = Path(__file__).parent.parent / "state"


def _state_path(schema_name: SchemaName) -> Path:
    return _STATE_DIR / f"{schema_name}_id_state.json"


def load_id_state(schema_name: SchemaName) -> IdState:
    """
    Load ID state for a schema; if none exists, start from zeros.
    """
    path = _state_path(schema_name)
    if not path.exists():
        return IdState()

    data = json.loads(path.read_text(encoding="utf-8"))
    return IdState(
        customer_next_index=data.get("customer_next_index", 0),
        survey_next_index=data.get("survey_next_index", 0),
        response_next_index=data.get("response_next_index", 0),
    )


def save_id_state(schema_name: SchemaName, state: IdState) -> None:
    """
    Persist ID state to disk.
    """
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = _state_path(schema_name)
    path.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")