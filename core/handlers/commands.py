# core/handlers/commands.py
import sys
import os
import urllib.parse
import uuid
from pyrogram import Client, filters
from pyrogram.types import Message
import config

from core.ui.dashboard import build_dashboard_text, build_dashboard_kb
from core.state.models import Job, Stage
from core.state.queues import download_queue
from core.pipeline.manager import transition_stage

# Global flag to pause/resume workers
BOT_PAUSED = False

def register_commands(app: Client):
    
    @app.on_message(filters.command(["start", "dashboard"]) & filters.user(config.OWNER_ID))
    async def init_dashboard(client: Client, msg: Message):
        """Spawns the main pinned dashboard."""
        await msg.reply(
            build_dashboard_text(page=0),
            reply_markup=build_dashboard_kb(page=0)
        )

    @app.on_message(filters.command("update") & filters.user(config.OWNER_ID))
    async def trigger_hot_reload(client: Client, msg: Message):
        """Signals the watchdog script to execute a git pull."""
        await msg.reply_text("🔄 Preparing environment shutdown sequence. Shifting control to Watchdog...")
        try:
            await client.stop(block=False)
        except Exception:
            pass
        sys.stdout.flush()
        os._exit(5) 

    @app.on_message(filters.command("stop") & filters.user(config.OWNER_ID))
    async def stop_bot(client: Client, msg: Message):
        """Pauses workers from picking up new jobs."""
        global BOT_PAUSED
        BOT_PAUSED = True
        await msg.reply("🛑 **Bot Paused.** Workers will finish current tasks but stop accepting new ones.")

    @app.on_message(filters.command("resume") & filters.user(config.OWNER_ID))
    async def resume_bot(client: Client, msg: Message):
        """Resumes background workers."""
        global BOT_PAUSED
        BOT_PAUSED = False
        await msg.reply("✅ **Bot Resumed.** Workers are back online.")

    @app.on_message(filters.command("log") & filters.user(config.OWNER_ID))
    async def get_job_log(client: Client, msg: Message):
        """Fetches the trace.log for a specific Job ID."""
        try:
            job_id = msg.text.split(" ")[1].strip()
        except IndexError:
            return await msg.reply("⚠️ Usage: `/log JOB_12345678`")
            
        target_dir = config.JOBS_DIR / job_id
        log_file = target_dir / "trace.log"
        
        if log_file.exists():
            await msg.reply_document(document=str(log_file), caption=f"📄 Trace log for `{job_id}`")
        else:
            await msg.reply(f"❌ No log found for `{job_id}`. It may have been cleaned up or never existed.")

    @app.on_message(filters.text & filters.user(config.OWNER_ID) & ~filters.command(["start", "dashboard", "update", "stop", "resume", "log"]))
    async def native_link_catcher(client: Client, msg: Message):
        """Catches URLs, generates a Job, and pushes it to the Download Queue."""
        url = next((w for w in msg.text.split() if w.startswith("http") or w.startswith("magnet:?")), None)
        if not url:
            return

        # 1. Generate unique Job ID and create working directory
        job_id = f"JOB_{uuid.uuid4().hex[:8].upper()}"
        work_dir = config.JOBS_DIR / job_id
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Build the Job payload
        job = Job(
            job_id=job_id,
            url=url,
            quality="720", 
            source="telegram_direct",
            work_dir=work_dir
        )
        
        # 3. Transition state and push to the queue
        transition_stage(job, Stage.QUEUED)
        await download_queue.put(job)
        
        # 4. Notify the user
        await msg.reply(
            f"📥 **Job Queued!**\n"
            f"🔗 `{url}`\n"
            f"🆔 `{job_id}`\n\n"
            f"*(Check your /dashboard to see it moving!)*"
        )