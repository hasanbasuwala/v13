# core/workers/download_worker.py
import asyncio
from core.state.queues import download_queue, encode_queue
from core.state.models import Job, Stage
from core.state.persistence import write_trace
from core.pipeline.manager import transition_stage
from core.downloader.strategy import execute_strategy

# Import commands to access the BOT_PAUSED flag
from core.handlers import commands

async def download_worker(worker_id: int) -> None:
    """Background worker that pulls jobs and routes them to download engines."""
    print(f"📥 Download Worker {worker_id} online...")
    
    while True:
        # Respect the /stop command
        if commands.BOT_PAUSED:
            await asyncio.sleep(2)
            continue
            
        job: Job = await download_queue.get()
        
        write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] Picked up job.")
        transition_stage(job, Stage.DOWNLOADING)
        
        try:
            # We use yt_dlp_primary as the default strategy for now
            success = await execute_strategy("yt_dlp_primary", job)
            
            if success:
                write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] ✅ Download complete.")
                transition_stage(job, Stage.DOWNLOADED)
                await encode_queue.put(job)
            else:
                write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] ❌ Download exhausted all retries.")
                transition_stage(job, Stage.FAILED)
                
        except Exception as e:
            write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] Critical crash: {e}")
            transition_stage(job, Stage.FAILED)
            
        finally:
            download_queue.task_done()