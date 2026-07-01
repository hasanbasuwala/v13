# test_worker.py
import asyncio
import shutil
import config
from core.state.models import Job, Stage
from core.state.queues import download_queue, encode_queue
from core.workers.download_worker import download_worker
from core.pipeline.scheduler import queue_for_download

async def run_worker_test():
    print("🚀 Initiating Async Worker Pipeline Test...")

    job_id = "TEST_WORKER_01"
    work_dir = config.JOBS_DIR / job_id
    
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    test_job = Job(
        job_id=job_id,
        url="https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4",
        quality="720", 
        source="test_script",
        work_dir=work_dir
    )

    # 1. Start the worker in the background (exactly how app.py will do it)
    worker_task = asyncio.create_task(download_worker(worker_id=1))

    # 2. Add the job to the queue
    print(f"📥 Queuing Job {job_id} for download...")
    await queue_for_download(test_job)

    # 3. Wait for the download queue to empty out
    await download_queue.join()
    print("✅ Download queue is completely empty.")

    # 4. Check if the worker successfully pushed the job to the encode queue
    if not encode_queue.empty():
        encoded_job = await encode_queue.get()
        print(f"✅ Encoder Queue received job: {encoded_job.job_id}")
    else:
        print("❌ Encoder Queue is empty. The worker failed to route the job.")

    # Clean up the background task so the script can exit cleanly
    worker_task.cancel()

    print("\n--- 📄 Subsystem Trace Log ---")
    trace_file = work_dir / "trace.log"
    if trace_file.exists():
        print(trace_file.read_text(encoding="utf-8").strip())
    print("------------------------------")

if __name__ == "__main__":
    asyncio.run(run_worker_test())
