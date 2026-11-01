import os
from typing import Dict, Any

PROMPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prompts"))

_PROMPT_CACHE: Dict[str, str] = {}


def load_prompt(name: str, **kwargs: Any) -> str:
    """
    Loads a prompt template by filename and formats it with provided kwargs.
    Templates are cached in memory.
    """
    if not name.endswith(".txt"):
        name = f"{name}.txt"

    if name not in _PROMPT_CACHE:
        file_path = os.path.join(PROMPT_DIR, name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt template not found at {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            _PROMPT_CACHE[name] = f.read()

    template = _PROMPT_CACHE[name]
    if kwargs:
        return template.format(**kwargs)
    return template
