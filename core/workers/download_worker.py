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
            # 1. Try yt-dlp first (Safely wrapped in its own try/except)
            try:
                success = await execute_strategy("yt_dlp_primary", job)
            except Exception as e:
                # Catch the yt-dlp format error so it doesn't crash the whole worker!
                write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] yt-dlp engine crashed: {e}")
                success = False
            
            # 2. If it fails, fallback to aria2 directly
            if not success:
                write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] yt-dlp failed, falling back to aria2...")
                try:
                    success = await execute_strategy("aria2_direct", job)
                except Exception as e:
                    write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] aria2 engine crashed: {e}")
                    success = False
            
            # 3. Route to next stage based on outcome
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
            # This now only catches extreme system-level errors
            write_trace(job.work_dir, f"[WORKER-DL-{worker_id}] Critical unhandled crash: {e}")
            transition_stage(job, Stage.FAILED)
            await send_failure_log(app, job, "Worker System Crash")
            
        finally:
            download_queue.task_done()