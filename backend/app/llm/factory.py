import logging
from typing import Optional
from app.core.config import settings
from app.llm.base import BaseLLMProvider
from app.llm.gemini import GeminiProvider
from app.llm.openai import OpenAIProvider
from app.llm.mock import MockLLMProvider

logger = logging.getLogger(__name__)


def get_llm_provider(
    provider_override: Optional[str] = None,
    model_override: Optional[str] = None,
) -> BaseLLMProvider:
    """
    Factory function to retrieve configured LLM provider.
    Fallback to MockLLMProvider if keys are missing or provider set to 'mock'.
    """
    provider_name = (provider_override or settings.LLM_PROVIDER).lower()
    model_name = model_override or settings.LLM_MODEL

    if provider_name == "gemini":
        if settings.GEMINI_API_KEY:
            logger.info("Initializing GeminiProvider with model: %s", model_name)
            return GeminiProvider(model_name=model_name)
        else:
            logger.warning("GEMINI_API_KEY not configured. Falling back to MockLLMProvider.")
            return MockLLMProvider(model_name=f"mock-{model_name}")

    elif provider_name == "openai":
        if settings.OPENAI_API_KEY:
            logger.info("Initializing OpenAIProvider with model: %s", model_name)
            return OpenAIProvider(model_name=model_name)
        else:
            logger.warning("OPENAI_API_KEY not configured. Falling back to MockLLMProvider.")
            return MockLLMProvider(model_name=f"mock-{model_name}")

    elif provider_name == "mock":
        return MockLLMProvider(model_name=model_name)

    logger.warning("Unrecognized provider '%s'. Defaulting to MockLLMProvider.", provider_name)
    return MockLLMProvider(model_name=model_name)
