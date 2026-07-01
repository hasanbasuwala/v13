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
        # Fails silently if the text hasn't changed or we hit a rate limit
        pass

async def send_final_log(app: Client, job: Job, final_status: str):
    """Sends the trace.log document to the bot owner for diagnosis."""
    if not job.ui_chat_id:
        return
        
    log_file = job.work_dir / "trace.log"
    if log_file.exists():
        try:
            await app.send_document(
                chat_id=job.ui_chat_id,
                document=str(log_file),
                caption=f"{final_status} Log for `{job.job_id}`\n**{job.title or 'No Title'}**"
            )
        except Exception:
            pass