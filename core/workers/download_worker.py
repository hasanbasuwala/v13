# core/workers/download_worker.py
import asyncio
from core.state.queues import download_queue, encode_queue
from core.state.models import Job, Stage
from core.state.persistence import write_trace
from core.pipeline.manager import transition_stage
from core.downloader.manager import process_download

async def download_worker(worker_id: int) -> None:
    """
    Background worker that pulls from the download queue,
    delegates to the orchestrator, and routes successful jobs to the encoder.
    """
    print(f"👷 Download Worker {worker_id} online and waiting for jobs...")
    
    while True:
        job: Job = await download_queue.get()
        
        write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] Picked up job from queue.")
        transition_stage(job, Stage.DOWNLOADING)
        
        try:
            # The worker makes no decisions; it just hands the job to the brain.
            success = await process_download(job)
            
            if success:
                write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] Download success. Routing to Encode Queue.")
                transition_stage(job, Stage.DOWNLOADED) 
                await encode_queue.put(job)
            else:
                write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] ❌ Download exhausted all retries.")
                transition_stage(job, Stage.FAILED)
                
        except Exception as e:
            write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] Critical unhandled worker crash: {e}")
            transition_stage(job, Stage.FAILED)
            
        finally:
            # Notify the queue that the task is complete to prevent deadlocks
            download_queue.task_done()
