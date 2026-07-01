# app.py
import asyncio
from pyrogram import Client
from pyrogram import idle
import config

# Import Handlers
from core.handlers.commands import register_commands
from core.handlers.callbacks import register_callbacks

# Import Workers
from core.workers.download_worker import download_worker
from core.workers.encode_worker import encode_worker
from core.workers.upload_worker import upload_worker

async def main():
    print("🚀 Booting Stealth Bot v13 Architecture...")

    # 1. Initialize Telegram Client
    app = Client(
        "stealth_bot_session",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        workdir=str(config.BASE_DIR)
    )

    # 2. Register UI Handlers
    register_commands(app)
    register_callbacks(app)

    # 3. Start Telegram Client
    await app.start()
    print("✅ Pyrogram Client Authenticated and Online.")

    # 4. Spawn Asynchronous Background Workers
    # You can easily scale these up later (e.g., spawn 3 downloaders, 2 encoders)
    print("👷 Spawning Subsystem Workers...")
    worker_tasks = [
        asyncio.create_task(download_worker(worker_id=1)),
        asyncio.create_task(encode_worker(worker_id=1)),
        asyncio.create_task(upload_worker(app, worker_id=1))
    ]

    print("🛡️ Bot is fully operational. Awaiting links...")
    
    # 5. Keep the bot running until forced to stop (Ctrl+C)
    await idle()

    # 6. Graceful Shutdown
    print("\n🛑 Shutting down. Cancelling workers...")
    for task in worker_tasks:
        task.cancel()
    
    await app.stop()
    print("💤 Goodnight!")

if __name__ == "__main__":
    # Use Pyrogram's built-in event loop management
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass