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

# --- DIRECTORIES ---
CACHE_DIR = Path("SysCache")
JOBS_DIR = CACHE_DIR / "jobs"

async def initialize_system_hub(app: Client, chat_id: int):
    """Sends the Mainframe dashboard and pins it to the top of the chat."""
    text = build_dashboard_text()
    markup = build_dashboard_kb()
    hub_message = await app.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    try:
        await app.pin_chat_message(
            chat_id=chat_id, 
            message_id=hub_message.id, 
            disable_notification=True,
            both_sides=True
        )
    except Exception as e:
        log_stealth(f"[⚠️] Could not pin Mainframe: {e}", new_line=True)
    return hub_message.id

async def main():
    log_stealth("[🚀] IGNITION SEQUENCE INITIATED", new_line=True)
    
    app = Client(
        "stealth_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="core.handlers") 
    )
    
    app.add_handler(CallbackQueryHandler(handle_ui_callbacks))
    
    download_queue = asyncio.Queue()
    
    await app.start()
    log_stealth("[🌐] TELEGRAM CONNECTION ESTABLISHED", new_line=True)
    
    await initialize_system_hub(app, ADMIN_CHAT_ID)
    asyncio.create_task(registry_heartbeat(CACHE_DIR))
    
    # --- FIXED: Passing download_queue first, then app ---
    for _ in range(3): 
        asyncio.create_task(download_worker(download_queue, app))
        
    log_stealth(f"[🛡️] STEALTH_BOT_V13.1 | ENGINE: ONLINE", new_line=True)
    
    await idle()
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
