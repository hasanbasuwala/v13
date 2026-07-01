import asyncio
from pathlib import Path
from pyrogram import Client, idle
from pyrogram.handlers import CallbackQueryHandler

# --- CORE IMPORTS ---
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID as ADMIN_CHAT_ID
from core.state.registry import Global_Registry
from core.state.persistence import log_stealth, registry_heartbeat
from core.ui.dashboard import build_dashboard_text, build_dashboard_kb
from core.ui.callbacks import handle_ui_callbacks

# --- WORKER IMPORTS ---
from core.workers.download_worker import download_worker
# from core.workers.encode_worker import encode_worker
# from core.workers.upload_worker import upload_worker

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
    text = build_dashboard_text()
    markup = build_dashboard_kb()
    
    # Send the hub message
    hub_message = await app.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    
    # Pin it permanently
    try:
        await app.pin_chat_message(
            chat_id=chat_id, 
            message_id=hub_message.id, 
            disable_notification=True,
            both_sides=True  # <--- FIX FOR [400 BOT_ONESIDE_NOT_AVAIL]
        )
        log_stealth(f"[📍] Mainframe Pinned to Chat {chat_id}", new_line=True)
    except Exception as e:
        log_stealth(f"[⚠️] Could not pin Mainframe: {e}", new_line=True)
        
    return hub_message.id

# ==========================================
# MAIN APPLICATION IGNITION
# ==========================================

async def main():
    log_stealth("[🚀] IGNITION SEQUENCE INITIATED", new_line=True)
    
    # 1. Initialize Telegram Client using credentials from config.py
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
    
    # -> Worker Pool (Passing 'app' client to resolve previous TypeError)
    for _ in range(3): # 3 Parallel Download workers
        asyncio.create_task(download_worker(app, download_queue))
        
    # asyncio.create_task(encode_worker(app, encode_queue))
    # asyncio.create_task(upload_worker(app, upload_queue))
        
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
