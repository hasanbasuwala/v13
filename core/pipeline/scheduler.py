# core/pipeline/scheduler.py
from core.state.queues import download_queue, encode_queue, upload_queue
from core.state.persistence import write_trace
from core.state.models import Job

async def queue_for_download(job: Job) -> None:
    write_trace(job.work_dir, f"[SCHEDULER] Routing job {job.job_id} to download queue.")
    await download_queue.put(job)
