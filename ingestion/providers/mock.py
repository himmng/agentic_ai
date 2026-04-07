from typing import Any

from .base import BaseProvider


class MockProvider(BaseProvider):
    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        # Minimal, valid JSON the agent can parse
        return """
        {
          "comment": "This is a synthetic mock comment for testing.",
          "answers": [
            {"question_id": "Q1", "answer": "Mock answer 1."},
            {"question_id": "Q2", "answer": "Mock answer 2."}
          ],
          "tags": ["billing", "web"]
        }
        """