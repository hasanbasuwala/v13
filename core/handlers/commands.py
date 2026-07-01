# core/handlers/commands.py
import sys
import os
import json
import uuid
import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message
import config

from core.ui.dashboard import build_dashboard_text, build_dashboard_kb
from core.state.models import Job, Stage
from core.state.queues import download_queue
from core.pipeline.manager import transition_stage

BOT_PAUSED = False

def register_commands(app: Client):
    
    @app.on_message(filters.command(["start", "dashboard"]) & filters.user(config.OWNER_ID))
    async def init_dashboard(client: Client, msg: Message):
        await msg.reply(
            build_dashboard_text(page=0),
            reply_markup=build_dashboard_kb(page=0)
        )

    @app.on_message(filters.command("update") & filters.user(config.OWNER_ID))
    async def trigger_hot_reload(client: Client, msg: Message):
        await msg.reply_text("🔄 Preparing environment shutdown sequence. Shifting control to Watchdog...")
        try:
            await client.stop(block=False)
        except Exception:
            pass
        sys.stdout.flush()
        os._exit(5) 

    @app.on_message(filters.command("stop") & filters.user(config.OWNER_ID))
    async def stop_bot(client: Client, msg: Message):
        global BOT_PAUSED
        BOT_PAUSED = True
        await msg.reply("🛑 **Bot Paused.** Workers will finish current tasks but stop accepting new ones.")

    @app.on_message(filters.command("resume") & filters.user(config.OWNER_ID))
    async def resume_bot(client: Client, msg: Message):
        global BOT_PAUSED
        BOT_PAUSED = False
        await msg.reply("✅ **Bot Resumed.** Workers are back online.")

    @app.on_message(filters.command("log") & filters.user(config.OWNER_ID))
    async def get_job_log(client: Client, msg: Message):
        try:
            job_id = msg.text.split(" ")[1].strip()
        except IndexError:
            return await msg.reply("⚠️ Usage: `/log JOB_12345678`")
            
        target_dir = config.JOBS_DIR / job_id
        log_file = target_dir / "trace.log"
        
        if log_file.exists():
            await msg.reply_document(document=str(log_file), caption=f"📄 Trace log for `{job_id}`")
        else:
            await msg.reply(f"❌ No log found for `{job_id}`.")

    @app.on_message(filters.text & filters.user(config.OWNER_ID) & ~filters.command(["start", "dashboard", "update", "stop", "resume", "log"]))
    async def native_link_catcher(client: Client, msg: Message):
        url = next((w for w in msg.text.split() if w.startswith("http") or w.startswith("magnet:?")), None)
        if not url:
            return

        raw_caption = msg.text.replace(url, "").strip()
        job_id = f"JOB_{uuid.uuid4().hex[:8].upper()}"
        job_title = raw_caption if raw_caption else job_id
        
        work_dir = config.JOBS_DIR / job_id
        work_dir.mkdir(parents=True, exist_ok=True)
        
        meta_file = work_dir / "meta.json"
        meta_file.write_text(json.dumps({"title": job_