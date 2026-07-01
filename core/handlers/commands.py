import json
import uuid
from pathlib import Path
from pyrogram import Client, filters
from core.state.models import Job, Stage
from core.state.queues import download_queue
from core.state.persistence import log_stealth

@Client.on_message(filters.text & filters.private)
async def native_link_catcher(client, message):
    url = message.text.split()[0]
    job_id = f"JOB_{str(uuid.uuid4())[:8].upper()}"
    
    # 1. Initialize the Job
    new_job = Job(
        job_id=job_id,
        url=url,
        stage=Stage.QUEUED,
        work_dir=Path(f"SysCache/jobs/{job_id}"),
        title="Untitled_Media",
        display_title="Untitled_Media",
        tags=["#Default"]
    )
    
    # 2. Create the directory
    new_job.work_dir.mkdir(parents=True, exist_ok=True)
    
    # 3. Log to terminal
    log_stealth(f"[INTAKE] {job_id} | Title: {new_job.display_title} | Tags: {len(new_job.tags)}", new_line=True)
    
    # 4. Push to the Download Queue (The fix for your stalled pipeline)
    await download_queue.put(new_job)
    log_stealth(f"[🚀] {job_id} pushed to Download Queue", new_line=True)
    
    # 5. Confirm to User
    await message.reply_text(f"📥 **Job Queued!**\n🆔 `{job_id}`")

    # 6. Save metadata (Ensuring the JSON write is complete)
    meta_file = new_job.work_dir / "metadata.json"
    meta_file.write_text(json.dumps({"title": new_job.display_title, "url": new_job.url}))
