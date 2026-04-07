from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseGenerator(ABC):
    @abstractmethod
    def generate_one(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produce a single record matching the given schema.
        For enrichers, you can ignore this and expose explicit methods.
        """
        ...