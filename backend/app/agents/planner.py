import logging
from typing import Dict, Any, Optional, Tuple
from app.llm.base import BaseLLMProvider
from app.schemas.research import ResearchPlan
from app.services.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    def plan_research(
        self,
        research_question: str,
        depth: str = "standard",
        focus_context: Optional[str] = None
    ) -> Tuple[ResearchPlan, Dict[str, Any]]:
        target_counts = {
            "quick": 3,
            "standard": 5,
            "deep": 8,
        }
        task_count = target_counts.get(depth.lower(), 5)
        context_str = focus_context or "General comprehensive investigation."

        prompt = load_prompt(
            "planner",
            research_question=research_question,
            depth=depth,
            task_count=task_count,
            focus_context=context_str
        )

        logger.info("Planner Agent analyzing query: '%s' (depth=%s)", research_question, depth)
        plan, usage = self.llm.generate_structured(
            prompt=prompt,
            pydantic_class=ResearchPlan,
            system_prompt="You are a senior research planner who decomposes queries into atomic, structured investigations."
        )

        return plan, usage
