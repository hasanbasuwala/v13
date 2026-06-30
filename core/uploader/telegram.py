# core/uploader/telegram.py
import asyncio
from pathlib import Path
from pyrogram import Client
from pyrogram.errors import FloodWait
from core.state.models import Job
from core.state.persistence import write_trace
import config

async def upload_video(app: Client, job: Job, video_path: Path, thumb_path: Path = None) -> bool:
    """Safely pushes the encoded media to Telegram, handling flood waits."""
    write_trace(job.work_dir, "[UPLOADER] Initiating Telegram upload...")
    
    try:
        # Pushing to the OWNER_ID for now; later we will pull chat_id from meta.json
        await app.send_video(
            chat_id=config.OWNER_ID,
            video=str(video_path),
            thumb=str(thumb_path) if thumb_path and thumb_path.exists() else None,
            caption=f"✅ **Job Complete:** `{job.job_id}`",
            supports_streaming=True
        )
        write_trace(job.work_dir, "[UPLOADER] ✅ Upload successful.")
        return True
        
    except FloodWait as e:
        write_trace(job.work_dir, f"[UPLOADER] ⚠️ FloodWait: Sleeping for {e.value} seconds...")
        await asyncio.sleep(e.value)
        # Recursively retry after the flood wait expires
        return await upload_video(app, job, video_path, thumb_path)
        
    except Exception as e:
        write_trace(job.work_dir, f"[UPLOADER] ❌ Upload failed: {e}")
        return False
