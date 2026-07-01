# core/downloader/strategy.py
import asyncio
from core.state.registry import Global_Registry
from core.state.persistence import log_stealth, write_trace

async def execute_strategy(engine_name: str, job) -> bool:
    """Entry point for downloads. Registers the job before starting."""
    
    # 1. Register the job the second it hits the strategy layer
    await Global_Registry.register_job(job.job_id, {
        "id": job.job_id,
        "title": getattr(job, "display_title", job.title),
        "stage": "queued",
        "progress": 0,
        "work_dir": str(job.work_dir)
    })
    
    log_stealth(f"[➕] Job {job.job_id} Registered to Mainframe", new_line=True)
    
    try:
        # Update stage to downloading
        await Global_Registry.update_job(job.job_id, {"stage": "downloading"})
        
        # (Your existing engine call goes here, e.g., await engine.run(job))
        # Example: result = await ytdlp_engine.download(job)
        
        return True # Or return the actual engine result
        
    except Exception as e:
        # Full stack trace diagnostic injection
        write_trace(job.work_dir, f"[STRATEGY] Fatal crash during engine execution", exception=e)
        await Global_Registry.update_job(job.job_id, {"stage": "failed", "progress": 0})
        return False