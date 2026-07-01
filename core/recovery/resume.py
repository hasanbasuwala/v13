# core/recovery/resume.py
import json
import asyncio
from core.state.queues import download_queue, encode_queue, upload_queue
from core.state.models import Job, Stage
import config

async def recover_pending_jobs():
    """Scans the disk on boot for incomplete jobs and re-queues them."""
    print("🔍 Scanning disk for interrupted jobs...")
    
    if not config.JOBS_DIR.exists():
        return

    recovered_count = 0
    for folder in config.JOBS_DIR.iterdir():
        if not folder.is_dir():
            continue

        state_file = folder / "state.json"
        if not state_file.exists():
            continue

        try:
            state_data = json.loads(state_file.read_text())
            stage = state_data.get("stage")
            
            # Skip jobs that already finished or failed permanently
            if stage in [Stage.DONE.value, Stage.FAILED.value]:
                continue 

            # Reconstruct the Job model from the saved atomic state
            job = Job(
                job_id=state_data["job_id"],
                url=state_data["url"],
                quality="720", 
                source="recovery",
                work_dir=folder
            )

            print(f"♻️ Recovering Job {job.job_id} (Interrupted at: {stage})")
            
            # Intelligently route to the correct queue based on where it crashed
            if stage in [Stage.QUEUED.value, Stage.RESOLVING.value, Stage.DOWNLOADING.value]:
                await download_queue.put(job)
            elif stage in [Stage.DOWNLOADED.value, Stage.ENCODING.value]:
                await encode_queue.put(job)
            elif stage in [Stage.ENCODED.value, Stage.UPLOADING.value]:
                await upload_queue.put(job)
                
            recovered_count += 1
            
        except Exception as e:
            print(f"⚠️ Failed to recover {folder.name}: {e}")
            
    if recovered_count > 0:
        print(f"✅ Recovery complete. {recovered_count} stranded jobs re-queued.")
    else:
        print("✅ Recovery complete. No stranded jobs found.")
