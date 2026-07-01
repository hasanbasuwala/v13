# core/handlers/commands.py
import uuid
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import Message
import config
from core.state.models import Job, Stage
from core.state.queues import download_queue
from core.pipeline.manager import transition_stage
from core.ui.dashboard import build_dashboard_text, build_dashboard_kb

def register_commands(app: Client):
    # ... (keep /start, /dashboard, /update, /stop, /resume handlers)

    @app.on_message(filters.text & filters.user(config.OWNER_ID) & ~filters.command(["start", "dashboard", "update", "stop", "resume"]))
    async def native_link_catcher(client: Client, msg: Message):
        url = next((w for w in msg.text.split() if w.startswith("http")), None)
        if not url: return

        # 1. Create a unique Job ID
        job_id = f"JOB_{uuid.uuid4().hex[:6].upper()}"
        work_dir = config.JOBS_DIR / job_id
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Instantiate the Job
        new_job = Job(
            job_id=job_id,
            url=url,
            quality="720",
            source="user_paste",
            work_dir=work_dir
        )
        
        # 3. Transition to QUEUED and push to the Downloader
        transition_stage(new_job, Stage.QUEUED)
        await download_queue.put(new_job)
        
        await msg.reply(f"📥 **Job Queued!**\nID: `{job_id}`\nURL: `{url}`")