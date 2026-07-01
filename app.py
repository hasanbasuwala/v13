import asyncio
from pyrogram import Client, idle
import config

# Import Handlers & UI
from core.handlers.commands import register_commands

# Import Workers
from core.workers.download_worker import download_worker
from core.workers.encode_worker import encode_worker
from core.workers.upload_worker import upload_worker

# Import Recovery Subsystem (assuming these exist in your v13 architecture)
from core.recovery.cleaner import kill_zombie_processes
from core.recovery.resume import recover_pending_jobs

async def main():
    print("🚀 Booting Stealth Bot v13.1 Architecture...")

    # 1. System Cleanup
    kill_zombie_processes()

    # 2. Initialize Telegram Client
    app = Client(
        "stealth_bot_session",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        workdir=str(config.BASE_DIR)
    )

    # 3. Register UI Handlers
    register_commands(app)

    # 4. Start Telegram Client
    await app.start()
    print("✅ Pyrogram Client Authenticated and Online.")

    # 5. Recover stranded jobs from previous crashes
    await recover_pending_jobs()

    # 6. Spawn Asynchronous Background Workers
    print("👷 Spawning Subsystem Workers...")
    worker_tasks = [
        asyncio.create_task(download_worker(app, worker_id=1)), # <-- Passed 'app' here
        asyncio.create_task(encode_worker(app, worker_id=1)),   # <-- Passed 'app' here
        asyncio.create_task(upload_worker(app, worker_id=1))    # <-- Passed 'app' here
    ]

    print("🛡️ Bot is fully operational. Awaiting links...")
    
    # 7. Keep the bot running until forced to stop (Ctrl+C)
    await idle()

    # 8. Graceful Shutdown
    print("\n🛑 Shutting down. Cancelling workers...")
    for task in worker_tasks:
        task.cancel()
    
    await app.stop()
    print("💤 Goodnight!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
