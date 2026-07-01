# test_encoder.py
import asyncio
import shutil
import subprocess
import config
from core.state.models import Job, Stage
from core.state.queues import encode_queue, upload_queue
from core.workers.encode_worker import encode_worker
from core.pipeline.manager import transition_stage

async def run_encoder_test():
    print("🚀 Initiating Async FFmpeg Encoder Worker Test...")
    
    job_id = "TEST_ENC_01"
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
        
    # 1. Generate a 3-second dummy video to act as our "downloaded" media
    dummy_file = work_dir / "dummy_input.mkv"
    print("🎬 Generating a 3-second dummy .mkv video for FFmpeg to process...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=3:size=640x360:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=3",
        "-c:v", "libx264", "-c:a", "aac", str(dummy_file)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 2. Start the worker in the background
    worker_task = asyncio.create_task(encode_worker(worker_id=1))
    
    # 3. Add the job to the encode queue
    transition_stage(test_job, Stage.DOWNLOADED)
    await encode_queue.put(test_job)
    
    # 4. Wait for the queue to empty
    await encode_queue.join()
    print("✅ Encode queue is completely empty.")
    
    # 5. Validate the results
    if not upload_queue.empty():
        ready_job = await upload_queue.get()
        print(f"✅ Upload Queue received job: {ready_job.job_id}")
        
        # Strictly verify the generated files on disk
        enc_file = work_dir / f"{job_id}_enc.mp4"
        thumb_file = work_dir / f"{job_id}_thumb.jpg"
        
        if enc_file.exists():
            print(f"✅ Remuxed MP4 file verified on disk: {enc_file.name}")
        if thumb_file.exists():
            print(f"✅ Extracted thumbnail verified on disk: {thumb_file.name}")
    else:
        print("❌ Upload Queue is empty. The worker failed to route the job.")
        
    worker_task.cancel()
    
    print("\n--- 📄 Subsystem Trace Log ---")
    trace_file = work_dir / "trace.log"
    if trace_file.exists():
        print(trace_file.read_text(encoding="utf-8").strip())
    print("------------------------------")

if __name__ == "__main__":
    asyncio.run(run_encoder_test())
