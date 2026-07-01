# core/uploader/telegram.py
import asyncio
from pathlib import Path
from pyrogram import Client
from pyrogram.errors import FloodWait
from core.state.models import Job
from core.state.persistence import write_trace
from core.uploader.metadata import extract_video_metadata
from core.ui.progress import upload_progress_callback
import config

async def upload_video(app: Client, job: Job, video_path: Path, thumb_path: Path = None) -> bool:
    """Uploads the media directly to the target channel with advanced metadata."""
    write_trace(job.work_dir, "[UPLOADER] Extracting metadata for Telegram...")
    
    # 1. Grab advanced metadata
    width, height, duration = await extract_video_metadata(video_path)
    write_trace(job.work_dir, f"[UPLOADER] Metadata parsed: {width}x{height} | {duration}s")
    
    try:
        # 2. Push to the Channel
        await app.send_video(
            chat_id=config.TARGET_CHANNEL_ID,  # <--- Now routes to the Channel
            video=str(video_path),
            thumb=str(thumb_path) if thumb_path and thumb_path.exists() else None,
            caption=f"✅ **{job.job_id}**\n`{job.url}`",
            supports_streaming=True,
            width=width,
            height=height,
            duration=duration,
            progress=upload_progress_callback, # <--- Live Dashboard Progress
            progress_args=(job.job_id,)
        )
        write_trace(job.work_dir, "[UPLOADER] ✅ Uploaded to Channel successfully.")
        return True
        
    except FloodWait as e:
        write_trace(job.work_dir, f"[UPLOADER] ⚠️ FloodWait: Sleeping for {e.value} seconds...")
        await asyncio.sleep(e.value)
        return await upload_video(app, job, video_path, thumb_path)
        
    except Exception as e:
        write_trace(job.work_dir, f"[UPLOADER] ❌ Channel upload failed: {e}")
        return False