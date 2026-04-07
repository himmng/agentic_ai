from typing import Any, Dict

import jsonschema


class JsonSchemaValidator:
    def __init__(self, schema: Dict[str, Any]):
        self._schema = schema

    def validate(self, record: Dict[str, Any]) -> None:
        jsonschema.validate(instance=record, schema=self._schema)