# app.py (Additions to your main file)
import asyncio
from pathlib import Path
from pyrogram import Client
from core.state.registry import Global_Registry
from core.state.persistence import log_stealth, registry_heartbeat
from core.ui.render import generate_mainframe_dashboard

async def run_resume_auditor(cache_dir: Path):
    """Scans the directory for orphaned jobs and registers them as PENDING or RESUMED."""
    log_stealth("[⚙️] Running Session Reconciliation...", new_line=True)
    
    # Example logic: Scan your job folders
    if cache_dir.exists():
        for job_folder in cache_dir.iterdir():
            if job_folder.is_dir():
                job_id = job_folder.name
                # Register found jobs back into the mainframe as pending recovery
                await Global_Registry.register_job(job_id, {
                    "id": job_id,
                    "stage": "queued", # Defaulting to queued for safety
                    "progress": 0,
                    "work_dir": str(job_folder)
                })
                log_stealth(f"[🔄] Recovered Job: {job_id}", new_line=True)

async def initialize_system_hub(app: Client, chat_id: int):
    """Sends the Mainframe dashboard and pins it to the top of the chat."""
    stats = {"downloading": 0, "waiting_proc": 0, "processing": 0, "waiting_up": 0, "uploading": 0, "disk_usage": "Scanning..."}
    
    # Generate the root dashboard
    text, markup = generate_mainframe_dashboard(stats, current_filter="ROOT")
    
    # Send the hub message
    hub_message = await app.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    
    # Pin it permanently
    try:
        await app.pin_chat_message(chat_id=chat_id, message_id=hub_message.id, disable_notification=True)
        log_stealth(f"[📍] Mainframe Pinned to Chat {chat_id}", new_line=True)
    except Exception as e:
        log_stealth(f"[⚠️] Could not pin Mainframe: {e}", new_line=True)
        
    return hub_message.id

# --- IN YOUR MAIN ASYNC FUNCTION ---
# async def main():
#     app = Client(...)
#     await app.start()
#     
#     # 1. Run Auditor
#     await run_resume_auditor(Path("SysCache/jobs"))
#     
#     # 2. Pin Mainframe (Replace 'YOUR_CHAT_ID' with your actual Telegram User ID)
#     await initialize_system_hub(app, YOUR_CHAT_ID)
#     
#     # 3. Start Heartbeat in background
#     asyncio.create_task(registry_heartbeat(Path("SysCache")))
#     
#     # (Start your workers here)