# core/workers/download_worker.py
import asyncio
from core.state.registry import Global_Registry
from core.state.persistence import log_stealth, write_trace

async def download_worker(queue: asyncio.Queue, app):
    """Background worker that reports to the Global Registry."""
    while True:
        job = await queue.get()
        
        # Pull the last known UI progress to prevent API spam
        job_data = await Global_Registry.get_job(job.job_id)
        last_ui_progress = job_data.get("progress", 0) if job_data else 0
        
        log_stealth(f"[📥] Worker picked up {job.job_id}", new_line=True)
        
        try:
            # --- SIMULATED DOWNLOAD LOOP ---
            # You will inject this logic into your actual download callback loop (e.g., yt-dlp hook)
            for current_progress in range(1, 101):
                
                # 1. Update the SILENT registry (so the terminal is always accurate)
                await Global_Registry.update_job(job.job_id, {"progress": current_progress})
                log_stealth(f"📥 {job.job_id} Downloading: {current_progress}%", new_line=False)
                
                # 2. Update the LOUD UI (Only trigger Telegram edit if +10% to avoid FloodWait)
                if current_progress >= (last_ui_progress + 10) or current_progress == 100:
                    last_ui_progress = current_progress
                    # Note: We will hook this to the actual Telegram UI edit function in Phase 4
                    
                await asyncio.sleep(0.1) # Simulating download time
                
            # Stage Complete
            log_stealth(f"[✅] {job.job_id} Download Complete", new_line=True)
            await Global_Registry.update_job(job.job_id, {"stage": "waiting_proc"})
            
            # (Pass to your encode_queue here)
            
        except Exception as e:
            write_trace(job.work_dir, f"[DOWNLOAD_WORKER] Crash on job {job.job_id}", exception=e)
            await Global_Registry.update_job(job.job_id, {"stage": "failed"})
            log_stealth(f"[❌] {job.job_id} Failed. See trace.log", new_line=True)
            
        finally:
            queue.task_done()