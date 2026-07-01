# core/ui/progress.py
from core.state.registry import live_progress

async def upload_progress_callback(current: int, total: int, job_id: str):
    """Feeds Pyrogram's live upload bytes into the dashboard memory registry."""
    if total == 0:
        return
        
    percent = (current / total) * 100
    
    # Update the live registry so the dashboard sees it instantly
    if job_id in live_progress:
        live_progress[job_id]["pct"] = percent
        live_progress[job_id]["stage"] = "Uploading to Channel..."