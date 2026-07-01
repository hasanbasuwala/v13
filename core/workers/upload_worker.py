# core/workers/upload_worker.py
import asyncio
from pyrogram import Client
from core.state.queues import upload_queue
from core.state.models import Job, Stage
from core.state.persistence import write_trace
from core.pipeline.manager import transition_stage
from core.uploader.telegram import upload_video
from core.handlers import commands
from core.ui.notifications import update_job_card, send_failure_log

async def upload_worker(app: Client, worker_id: int) -> None:
    print(f"🚀 Upload Worker {worker_id} online...")
    
    while True:
        if commands.BOT_PAUSED:
            await asyncio.sleep(2)
            continue
            
        job: Job = await upload_queue.get()
        write_trace(job.work_dir, f"[WORKER-UP-{worker_id}] Picked up job.")
        transition_stage(job, Stage.UPLOADING)
        await update_job_card(app, job, "Uploading to Telegram... 📤")
        
        try:
            enc_file = job.work_dir / f"{job.job_id}_enc.mp4"
            thumb_file = job.work_dir / f"{job.job_id}_thumb.jpg"
            
            if not enc_file.exists():
                raise FileNotFoundError("Encoded MP4 is missing from the working directory.")
                
            success = await upload_video(app, job, enc_file, thumb_file)
            
            if success:
                write_trace(job.work_dir, f"[WORKER-UP-{worker_id}] ✅ Job fully completed!")
                transition_stage(job, Stage.DONE)
                await update_job_card(app, job, "Done ✅")
            else:
                write_trace(job.work_dir, f"[WORKER-UP-{worker_id}] ❌ Upload exhausted/failed.")
                transition_stage(job, Stage.FAILED)
                await send_failure_log(app, job, "Telegram Upload Failed")
                
        except Exception as e:
            write_trace(job.work_dir, f"[WORKER-UP-{worker_id}] Critical crash: {e}")
            transition_stage(job, Stage.FAILED)
            await send_failure_log(app, job, "Uploader Worker Crash")
            
        finally:
            upload_queue.task_done()