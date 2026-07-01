# test_uploader.py
import asyncio
import shutil
from pathlib import Path
from pyrogram import Client
import config
from core.state.models import Job, Stage
from core.state.queues import upload_queue
from core.workers.upload_worker import upload_worker
from core.pipeline.manager import transition_stage

async def run_uploader_test():
    print("🚀 Initiating Telegram Uploader Test...")
    
    # 1. Initialize Pyrogram Client
    app = Client(
        "stealth_test_session",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        workdir=str(config.BASE_DIR)
    )
    
    job_id = "TEST_UP_01"
    work_dir = config.JOBS_DIR / job_id
    
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    
    test_job = Job(
        job_id=job_id,
        url="mock_url",
        quality="720",
        source="test_script",
        work_dir=work_dir
    )
    
    # 2. Steal the dummy files we made in the encoder test to simulate a finished encode
    old_enc_file = config.JOBS_DIR / "TEST_ENC_01" / "TEST_ENC_01_enc.mp4"
    old_thumb_file = config.JOBS_DIR / "TEST_ENC_01" / "TEST_ENC_01_thumb.jpg"
    
    if not old_enc_file.exists():
        print("❌ Error: Could not find the dummy video from the previous test.")
        return
        
    shutil.copy(old_enc_file, work_dir / f"{job_id}_enc.mp4")
    if old_thumb_file.exists():
        shutil.copy(old_thumb_file, work_dir / f"{job_id}_thumb.jpg")
        
    print("🎬 Mock encoded files staged successfully.")
    
    # 3. Start the Pyrogram client
    await app.start()
    
    # 4. Start the upload worker in the background, passing the app instance
    worker_task = asyncio.create_task(upload_worker(app, worker_id=1))
    
    # 5. Push the job to the upload queue
    transition_stage(test_job, Stage.ENCODED)
    await upload_queue.put(test_job)
    
    # 6. Wait for the queue to process
    print("📤 Pushing to Telegram API...")
    await upload_queue.join()
    
    # 7. Cleanup
    worker_task.cancel()
    await app.stop()
    
    print("\n--- 📄 Subsystem Trace Log ---")
    trace_file = work_dir / "trace.log"
    if trace_file.exists():
        print(trace_file.read_text(encoding="utf-8").strip())
    print("------------------------------")
    print("✅ If you received the video in Telegram, the upload pipeline is flawless!")

if __name__ == "__main__":
    asyncio.run(run_uploader_test())
