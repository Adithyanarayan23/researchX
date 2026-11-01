import asyncio
import logging
from app.workers.celery_app import celery_app
from app.services.job_manager import execute_research_workflow

logger = logging.getLogger(__name__)


@celery_app.task(name="execute_research_job_task")
def execute_research_job_task(job_id: str):
    logger.info("Celery task received for research job: %s", job_id)
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Running in nested event loop
        new_loop = asyncio.new_event_loop()
        new_loop.run_until_complete(execute_research_workflow(job_id))
        new_loop.close()
    else:
        loop.run_until_complete(execute_research_workflow(job_id))
    return {"job_id": job_id, "status": "processed"}
