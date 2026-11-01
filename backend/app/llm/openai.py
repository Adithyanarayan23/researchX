import json
import re
from typing import Type, TypeVar, Tuple, Dict, Any, Optional, List
from pydantic import BaseModel
from openai import OpenAI
from app.llm.base import BaseLLMProvider
from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY or "dummy-key-for-local"
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self.model_name = model_name or settings.LLM_MODEL
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> Tuple[str, Dict[str, Any]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content or ""
        in_tokens = response.usage.prompt_tokens if response.usage else 0
        out_tokens = response.usage.completion_tokens if response.usage else 0

        usage = {
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "model": self.model_name,
        }
        return content, usage

    def generate_structured(
        self,
        prompt: str,
        pydantic_class: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
    ) -> Tuple[T, Dict[str, Any]]:
        schema_json = json.dumps(pydantic_class.model_json_schema(), indent=2)
        sys_instruction = system_prompt or "You are an expert AI research analysis system."
        full_sys_prompt = (
            f"{sys_instruction}\n\n"
            f"You MUST format your output strictly as valid JSON adhering to the following JSON Schema:\n"
            f"```json\n{schema_json}\n```\n"
            f"Respond ONLY with raw JSON. Do not include markdown ticks."
        )

        messages = [
            {"role": "system", "content": full_sys_prompt},
            {"role": "user", "content": prompt},
        ]

        try:
            # Attempt response_format json_object
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
        except Exception:
            # Fallback if provider doesn't support json_object format parameter
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
            )

        content = response.choices[0].message.content or "{}"
        match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", content, re.DOTALL)
        if match:
            clean_json = match.group(1)
        else:
            clean_json = content.strip()

        data = json.loads(clean_json)
        parsed = pydantic_class.model_validate(data)

        in_tokens = response.usage.prompt_tokens if response.usage else 0
        out_tokens = response.usage.completion_tokens if response.usage else 0

        usage = {
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "model": self.model_name,
        }
        return parsed, usage

    def get_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        except Exception:
            return [0.0] * settings.EMBEDDING_DIMENSION
