import asyncio
import os
from pathlib import Path
from pyrogram import Client, idle
from pyrogram.handlers import CallbackQueryHandler

# --- CORE IMPORTS ---
from core.state.registry import Global_Registry
from core.state.persistence import log_stealth, registry_heartbeat
from core.ui.render import generate_mainframe_dashboard
from core.ui.callbacks import handle_ui_callbacks

# --- WORKER IMPORTS ---
# Ensure these match your actual worker file structures
from core.workers.download_worker import download_worker
# from core.workers.encode_worker import encode_worker
# from core.workers.upload_worker import upload_worker

# --- CONFIGURATION ---
# Replace these with your actual credentials, or set them in your environment variables
API_ID = os.environ.get("API_ID", "YOUR_API_ID_HERE")
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH_HERE")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "123456789")) # <-- SET YOUR CHAT ID HERE

# --- DIRECTORIES ---
CACHE_DIR = Path("SysCache")
JOBS_DIR = CACHE_DIR / "jobs"

# ==========================================
# BOOTSTRAPPER & AUDITOR
# ==========================================

async def run_resume_auditor(cache_dir: Path):
    """Scans the directory for orphaned jobs and registers them as PENDING."""
    log_stealth("[⚙️] Running Session Reconciliation...", new_line=True)
    
    if cache_dir.exists():
        for job_folder in cache_dir.iterdir():
            if job_folder.is_dir():
                job_id = job_folder.name
                # Register found jobs back into the mainframe as pending recovery
                await Global_Registry.register_job(job_id, {
                    "id": job_id,
                    "stage": "queued",
                    "progress": 0,
                    "work_dir": str(job_folder)
                })
                log_stealth(f"[🔄] Recovered Job: {job_id} -> PENDING", new_line=True)
    else:
        # Create directories if this is a fresh start
        cache_dir.mkdir(parents=True, exist_ok=True)

async def initialize_system_hub(app: Client, chat_id: int):
    """Sends the Mainframe dashboard and pins it to the top of the chat."""
    stats = {"downloading": 0, "waiting_proc": 0, "processing": 0, "waiting_up": 0, "uploading": 0, "disk_usage": "Scanning..."}
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

# ==========================================
# MAIN APPLICATION IGNITION
# ==========================================

async def main():
    log_stealth("[🚀] IGNITION SEQUENCE INITIATED", new_line=True)
    
    # 1. Initialize Telegram Client
    # We use plugins to auto-load commands like your smart parser in commands.py
    app = Client(
        "stealth_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="core.handlers") 
    )
    
    # 2. Wire the UI Engine Callbacks
    app.add_handler(CallbackQueryHandler(handle_ui_callbacks))
    
    # 3. Initialize Queues (Decoupled Pipeline)
    download_queue = asyncio.Queue()
    encode_queue = asyncio.Queue()
    upload_queue = asyncio.Queue()
    
    # 4. Start Client
    await app.start()
    log_stealth("[🌐] TELEGRAM CONNECTION ESTABLISHED", new_line=True)
    
    # 5. Execute Bootstrapper
    await run_resume_auditor(JOBS_DIR)
    hub_message_id = await initialize_system_hub(app, ADMIN_CHAT_ID)
    
    # 6. Start Background Tasks
    
    # -> Heartbeat (State saving every 60s)
    asyncio.create_task(registry_heartbeat(CACHE_DIR))
    
    # -> Worker Pool (Adjust concurrency numbers here)
    for _ in range(3): # 3 Parallel Download workers
        asyncio.create_task(download_worker(download_queue, app))
        
    # (Uncomment these once you upgrade encode_worker and upload_worker using the Phase 3 template)
    # for _ in range(1): # 1 Encode worker (Protects CPU)
    #     asyncio.create_task(encode_worker(encode_queue, app))
    # for _ in range(1): # 1 Upload worker (Protects Telegram API limits)
    #     asyncio.create_task(upload_worker(upload_queue, app))
        
    log_stealth(f"[🛡️] STEALTH_BOT_V13.1 | ENGINE: ONLINE | QUEUE: 0", new_line=True)
    
    # 7. Keep bot running
    await idle()
    
    # 8. Clean Shutdown
    await app.stop()
    log_stealth("[🛑] SYSTEM SHUTDOWN COMPLETE", new_line=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Force closed by user.")