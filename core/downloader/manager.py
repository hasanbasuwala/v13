# core/downloader/manager.py
import traceback
import config
from core.state.models import Job
from core.state.persistence import write_trace
from core.pipeline.classifier import classify
from core.pipeline.retry import get_strategy
from core.downloader.strategy import execute_strategy

async def process_download(job: Job) -> bool:
    """Orchestrates the 6-stage fallback waterfall for a media asset."""
    classification = classify(job.url)
    write_trace(job.work_dir, f"[DOWNLOAD-MANAGER] URL classified as: {classification}")

    for attempt in range(1, config.MAX_RETRIES + 1):
        strategy_name = get_strategy(classification, attempt)
        
        if strategy_name == "pipeline_failure":
            write_trace(job.work_dir, "[DOWNLOAD-MANAGER] ❌ All download strategies exhausted.")
            return False
        
        write_trace(job.work_dir, f"[DOWNLOAD-MANAGER] Attempt {attempt} -> Routing to {strategy_name}")
        
        try:
            success = await execute_strategy(strategy_name, job)
            if success:
                write_trace(job.work_dir, f"[DOWNLOAD-MANAGER] ✅ {strategy_name} completed successfully.")
                return True
        except Exception as e:
            write_trace(job.work_dir, f"[DOWNLOAD-MANAGER] ⚠️ {strategy_name} failed: {str(e)}")
            write_trace(job.work_dir, traceback.format_exc())
            
    return False
