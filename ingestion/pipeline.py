from schemas.registry import SchemaRegistry
from generators.structured import StructuredGenerator
from sinks.jsonl import JsonlSink

def run(schema_name, n=10):
    registry = SchemaRegistry("schemas/definitions")
    schema = registry.get(schema_name)

    generator = StructuredGenerator(schema)
    sink = JsonlSink(f"{schema_name}.jsonl")

    for _ in range(n):
        record = generator.generate()
        sink.write(record)