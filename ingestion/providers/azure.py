import os
from typing import Any

from dotenv import load_dotenv
from .base import BaseProvider
from openai import AzureOpenAI  # pip install openai

load_dotenv()


class AzureOpenAIProvider(BaseProvider):
    """
    Azure OpenAI provider for text generation.
    Expects environment variables:
      AZURE_OPENAI_ENDPOINT
      AZURE_OPENAI_API_KEY
      AZURE_OPENAI_DEPLOYMENT
      (optional) AZURE_OPENAI_API_VERSION
    """

    def __init__(
        self,
        deployment_name: str | None = None,
        endpoint: str | None = None,
        api_key: str | None = None,
        api_version: str | None = None,
    ) -> None:
        self.deployment_name = deployment_name or os.environ["AZURE_OPENAI_DEPLOYMENT"]
        endpoint = endpoint or os.environ["AZURE_OPENAI_ENDPOINT"]
        api_key = api_key or os.environ["AZURE_OPENAI_API_KEY"]
        api_version = api_version or os.environ.get(
            "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
        )

        self._client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )

    def generate_text(self, prompt: str, **kwargs: Any) -> str:

        response = self._client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )

        text = response.choices[0].message.content or ""
        # Strip whitespace only; prompt must ensure output is pure JSON
        return text.strip()