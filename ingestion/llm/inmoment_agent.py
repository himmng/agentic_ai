import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from ..providers.base import BaseProvider


@dataclass
class InMomentTextResult:
    """
    Result from the InMoment LLM agent:
      - comment: main feedback text
      - answers: list of {question_id, answer}
      - tags: list of strings (e.g. billing, outage, etc.)
    """
    comment: str
    answers: List[Dict[str, Any]]
    tags: List[str]


class InMomentTextAgent:
    """
    LLM agent wrapper for InMoment text fields.

    It loads a prompt template from prompts/inmoment/prompt.txt and
    expects the model to return a JSON object:

      {
        "comment": "...",
        "answers": [
          {"question_id": "...", "answer": "..."},
          ...
        ],
        "tags": ["billing", "web"]
      }
    """

    def __init__(self, provider: BaseProvider) -> None:
        prompt_path = (
            Path(__file__).parent.parent
            / "prompts"
            / "inmoment"
            / "prompt.txt"
        )
        self._provider = provider
        self._prompt_template = prompt_path.read_text(encoding="utf-8")

    def generate(self, context: Dict[str, Any]) -> InMomentTextResult:
        """
        context may contain:
          - customer_id
          - nps
          - channel
          - complaint_type
          - complaint_time
          - responses (with question_id)
          - any other metadata you need for realism
        """
        prompt = self._build_prompt(context)
        raw = self._provider.generate_text(prompt)
        obj = self._parse_output(raw)
        return InMomentTextResult(
            comment=obj["comment"],
            answers=obj["answers"],
            tags=obj.get("tags", []),
        )

    # --- internal ---

    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Insert the JSON-encoded context into the prompt template.
        The template should contain a placeholder like {{context_json}}.
        """
        context_json = json.dumps(context, ensure_ascii=False)
        return self._prompt_template.replace("{{context_json}}", context_json)

    def _parse_output(self, raw: str) -> Dict[str, Any]:
        """
        Parse JSON from the LLM output and do basic validation.
        """
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"InMoment agent: invalid JSON output: {e}") from e

        if not isinstance(obj, dict):
            raise ValueError("InMoment agent: expected JSON object")

        comment = obj.get("comment")
        answers = obj.get("answers")
        tags = obj.get("tags", [])

        if not isinstance(comment, str):
            raise ValueError("InMoment agent: 'comment' must be a string")
        if not isinstance(answers, list):
            raise ValueError("InMoment agent: 'answers' must be a list")
        if not isinstance(tags, list):
            raise ValueError("InMoment agent: 'tags' must be a list")

        return {
            "comment": comment,
            "answers": answers,
            "tags": tags,
        }