# core/workers/download_worker.py
import asyncio
from pyrogram import Client
from core.state.queues import download_queue, encode_queue
from core.state.models import Job, Stage
from core.state.persistence import write_trace
from core.pipeline.manager import transition_stage
from core.downloader.strategy import execute_strategy
from core.handlers import commands
from core.ui.notifications import update_job_card, send_failure_log

async def download_worker(app: Client, worker_id: int) -> None:
    print(f"📥 Download Worker {worker_id} online...")
    
    while True:
        if commands.BOT_PAUSED:
            await asyncio.sleep(2)
            continue
            
        job: Job = await download_queue.get()
        write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] Picked up job.")
        transition_stage(job, Stage.DOWNLOADING)
        await update_job_card(app, job, "Downloading... ⏳")
        
        try:
            # 1. Try yt-dlp first
            success = await execute_strategy("yt_dlp_primary", job)
            
            # 2. If it fails, fallback to aria2 directly
            if not success:
                write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] yt-dlp failed, falling back to aria2...")
                success = await execute_strategy("aria2_direct", job)
            
            if success:
                write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] ✅ Download complete.")
                transition_stage(job, Stage.DOWNLOADED)
                await update_job_card(app, job, "Download Complete. Waiting for Encoder... ♻️")
                await encode_queue.put(job)
            else:
                write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] ❌ Download exhausted all retries.")
                transition_stage(job, Stage.FAILED)
                await send_failure_log(app, job, "Download Engines Exhausted")
                
        except Exception as e:
            write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] Critical crash: {e}")
            transition_stage(job, Stage.FAILED)
            await send_failure_log(app, job, "Worker Crash")
            
        finally:
            download_queue.task_done()