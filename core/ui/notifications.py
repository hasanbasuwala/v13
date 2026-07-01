# core/ui/notifications.py
from pyrogram import Client
from core.state.models import Job
import config

async def update_job_card(app: Client, job: Job, status_text: str):
    """Safely edits the original intake message to reflect the current stage."""
    if not job.ui_msg_id or not job.ui_chat_id:
        return
        
    try:
        card_text = (
            f"📺 **{job.title or job.job_id}**\n"
            f"🔗 `{job.url}`\n\n"
            f"🔄 **Status:** {status_text}"
        )
        await app.edit_message_text(
            chat_id=job.ui_chat_id,
            message_id=job.ui_msg_id,
            text=card_text
        )
    except Exception:
        # Fails silently if the message hasn't changed or if rate-limited by Telegram
        pass

async def send_failure_log(app: Client, job: Job, error_msg: str = "Pipeline exhausted."):
    """Automatically sends the trace.log back to the user if a job fails."""
    if not job.ui_chat_id:
        return
        
    try:
        log_file = job.work_dir / "trace.log"
        caption_text = f"❌ **Job Failed:** `{job.job_id}`\n⚠️ **Reason:** {error_msg}"
        
        if log_file.exists():
            await app.send_document(
                chat_id=job.ui_chat_id, 
                document=str(log_file), 
                caption=caption_text
            )
        else:
            await app.send_message(
                chat_id=job.ui_chat_id, 
                text=f"{caption_text}\n*(No trace log was generated)*"
            )
    except Exception:
        pass
