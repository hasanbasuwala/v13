# core/ui/notifications.py
from pyrogram import Client
from core.state.models import Job

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
        pass

async def send_failure_log(app: Client, job: Job, error_stage: str):
    """Automatically sends the trace.log to the user when a job fails."""
    if not job.ui_chat_id:
        return
        
    await update_job_card(app, job, f"Failed ❌ ({error_stage})")
    
    log_file = job.work_dir / "trace.log"
    if log_file.exists():
        try:
            await app.send_document(
                chat_id=job.ui_chat_id,
                document=str(log_file),
                caption=f"⚠️ **Job Failed:** `{job.job_id}`\nFailed during: `{error_stage}`"
            )
        except Exception as e:
            print(f"Could not send log document: {e}")
    else:
        try:
            await app.send_message(
                chat_id=job.ui_chat_id,
                text=f"⚠️ **Job Failed:** `{job.job_id}`\n*(No trace.log was found on disk)*"
            )
        except Exception:
            pass