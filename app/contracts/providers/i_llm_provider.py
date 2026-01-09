from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel

class ExtractionResult(BaseModel):
    """
    Summary: Result of the intent extraction phase.
    """
    is_search_required: bool
    search_query: Optional[str] = None
    reasoning: str

class ILLMProvider(ABC):
    """
    Summary: Interface for Large Language Model providers.
    """

    @abstractmethod
    async def generate_response(self, prompt: str, system_message: str) -> str:
        """
        Summary: Generates a natural language response.
        """

        pass

    @abstractmethod
    async def extract_intent(self, prompt: str) -> ExtractionResult:
        """
        Summary: Extracts structured intent from user input.
        """

        pass
