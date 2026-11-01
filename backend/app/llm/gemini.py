import json
import re
import warnings
from typing import Type, TypeVar, Tuple, Dict, Any, Optional, List
from pydantic import BaseModel

warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
from app.llm.base import BaseLLMProvider
from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided via environment or settings.")
        genai.configure(api_key=self.api_key)
        self.model_name = model_name or settings.LLM_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> Tuple[str, Dict[str, Any]]:
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt if system_prompt else None,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        response = model.generate_content(prompt)
        text = response.text or ""

        # Approximate token usage if not directly exposed
        in_tokens = len(prompt.split()) + (len(system_prompt.split()) if system_prompt else 0)
        out_tokens = len(text.split())
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            in_tokens = getattr(response.usage_metadata, "prompt_token_count", in_tokens)
            out_tokens = getattr(response.usage_metadata, "candidates_token_count", out_tokens)

        usage = {
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "model": self.model_name,
        }
        return text, usage

    def generate_structured(
        self,
        prompt: str,
        pydantic_class: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
    ) -> Tuple[T, Dict[str, Any]]:
        json_schema = json.dumps(pydantic_class.model_json_schema(), indent=2)
        augmented_prompt = (
            f"{prompt}\n\n"
            f"You MUST reply ONLY with a valid JSON object strictly complying with this JSON Schema:\n"
            f"```json\n{json_schema}\n```\n"
            f"Do not output any introductory or concluding markdown outside the JSON code block."
        )

        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt if system_prompt else None,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                response_mime_type="application/json",
            )
        )
        response = model.generate_content(augmented_prompt)
        text = response.text or "{}"

        # Clean JSON markdown if wrapped
        match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", text, re.DOTALL)
        if match:
            clean_json = match.group(1)
        else:
            clean_json = text.strip()

        data = json.loads(clean_json)
        parsed = pydantic_class.model_validate(data)

        in_tokens = len(augmented_prompt.split())
        out_tokens = len(text.split())
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            in_tokens = getattr(response.usage_metadata, "prompt_token_count", in_tokens)
            out_tokens = getattr(response.usage_metadata, "candidates_token_count", out_tokens)

        usage = {
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "model": self.model_name,
        }
        return parsed, usage

    def get_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model=f"models/{self.embedding_model}",
                content=text,
                task_type="retrieval_document"
            )
            return result.get("embedding", [0.0] * settings.EMBEDDING_DIMENSION)
        except Exception:
            return [0.0] * settings.EMBEDDING_DIMENSION
