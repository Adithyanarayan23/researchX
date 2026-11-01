from abc import ABC, abstractmethod
from typing import Type, TypeVar, Tuple, Dict, Any, Optional, List
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM operations.
    Decouples the agents from any specific provider (Gemini, OpenAI, Mock, etc.)
    """

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate text response.
        Returns: (response_text, usage_metadata)
        usage_metadata: {"input_tokens": int, "output_tokens": int, "model": str}
        """
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        pydantic_class: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
    ) -> Tuple[T, Dict[str, Any]]:
        """
        Generate structured output adhering to a Pydantic schema.
        Returns: (parsed_pydantic_instance, usage_metadata)
        """
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for semantic search.
        """
        pass
