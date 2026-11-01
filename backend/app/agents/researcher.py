import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from app.llm.base import BaseLLMProvider
from app.tools.search import search_web
from app.tools.fetcher import fetch_webpage
from app.services.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class ResearchAgent:
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    async def execute_task(
        self,
        task_id: str,
        sub_question: str,
        category: str = "general",
        existing_context: str = "",
        max_sources_to_fetch: int = 2
    ) -> Dict[str, Any]:
        """
        Executes an individual research task:
        1. Searches the web for relevant intelligence.
        2. Fetches high-value pages.
        3. Formulates evidence snippets.
        4. Synthesizes key observations.
        """
        logger.info("Research Agent executing task %s: '%s'", task_id, sub_question)

        # 1. Web search
        search_results = await search_web(sub_question, max_results=4)

        collected_sources: List[Dict[str, Any]] = []
        evidence_snippets: List[Dict[str, Any]] = []

        # 2. Collect sources & evidence snippets
        for res in search_results:
            source_data = {
                "url": res.get("url"),
                "title": res.get("title", "Untitled Source"),
                "domain": res.get("domain", "web"),
                "publisher": res.get("domain"),
                "source_type": res.get("source_type", "website"),
                "credibility_score": res.get("credibility_score", 0.70),
                "content": res.get("snippet", ""),
                "content_hash": None,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }
            collected_sources.append(source_data)

            # Create evidence snippet
            evidence_snippets.append({
                "task_id": task_id,
                "sub_question": sub_question,
                "source_url": res.get("url"),
                "source_title": res.get("title"),
                "domain": res.get("domain"),
                "credibility_score": res.get("credibility_score", 0.70),
                "snippet": res.get("snippet", ""),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            })

        # 3. Fetch full content for the top promising web pages
        pages_to_fetch = [s for s in collected_sources if s.get("url") and s["url"].startswith("http")][:max_sources_to_fetch]
        for src in pages_to_fetch:
            try:
                page_data = await fetch_webpage(src["url"], timeout=10)
                if page_data and page_data.get("content"):
                    src["content"] = page_data["content"]
                    src["content_hash"] = page_data["content_hash"]
                    src["title"] = page_data.get("title") or src["title"]
                    # Add additional extracted snippet from page body
                    body_sample = page_data["content"][:1000]
                    evidence_snippets.append({
                        "task_id": task_id,
                        "sub_question": sub_question,
                        "source_url": src["url"],
                        "source_title": src["title"],
                        "domain": src["domain"],
                        "credibility_score": src["credibility_score"],
                        "snippet": body_sample,
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception as e:
                logger.warning("Error fetching full page for %s: %s", src["url"], str(e))

        # 4. Synthesize observations using LLM
        retrieved_text = "\n\n".join([f"[{i+1}] {e['source_title']} ({e['domain']}): {e['snippet']}" for i, e in enumerate(evidence_snippets)])
        prompt = load_prompt(
            "researcher",
            sub_question=sub_question,
            category=category,
            context=existing_context or "Initial investigation phase.",
            retrieved_chunks=retrieved_text or "No external snippets retrieved."
        )

        obs_text, usage = self.llm.generate_text(
            prompt=prompt,
            system_prompt="You are a meticulous research analyst who grounds every statement directly in provided evidence.",
            temperature=0.2
        )

        return {
            "task_id": task_id,
            "sub_question": sub_question,
            "observations": obs_text,
            "sources": collected_sources,
            "evidence": evidence_snippets,
            "usage": usage,
        }
