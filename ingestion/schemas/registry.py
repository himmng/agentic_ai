import json
from pathlib import Path

class SchemaRegistry:
    def __init__(self, path):
        self.path = Path(path)
        self.schemas = self._load()

    def _load(self):
        schemas = {}
        for file in self.path.glob("*"):
            if file.suffix == ".json":
                schemas[file.stem] = json.loads(file.read_text())
        return schemas

    def get(self, name):
        return self.schemas[name]