from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        ...