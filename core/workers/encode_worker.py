# core/workers/encode_worker.py
import asyncio
from core.state.queues import encode_queue, upload_queue
from core.state.models import Job, Stage
from core.state.persistence import write_trace
from core.pipeline.manager import transition_stage
from core.encoder.transcode import safe_remux
from core.encoder.thumbnail import generate_thumbnail

async def encode_worker(worker_id: int) -> None:
    """Background worker that processes downloaded files through the FFmpeg sandbox."""
    print(f"🎬 Encode Worker {worker_id} online and waiting for jobs...")
    
    while True:
        job: Job = await encode_queue.get()
        
        write_trace(job.work_dir, f"[WORKER-ENC-{worker_id}] Picked up job for encoding.")
        transition_stage(job, Stage.ENCODING)
        
        try:
            # Locate the largest media file in the working directory (ignoring logs/metadata)
            dl_files = [f for f in job.work_dir.glob("*.*") if f.is_file() and f.suffix not in ['.json', '.log', '.part']]
            if not dl_files:
                raise FileNotFoundError("No media file found in working directory.")
                
            input_file = max(dl_files, key=lambda p: p.stat().st_size)
            
            # Define isolated output paths
            output_file = job.work_dir / f"{job.job_id}_enc.mp4"
            thumb_file = job.work_dir / f"{job.job_id}_thumb.jpg"
            
            # 1. Generate Thumbnail (Wait for it to finish, but failure won't kill the job)
            await generate_thumbnail(job, input_file, thumb_file)
            
            # 2. Remux the video safely using the FFmpeg sandbox
            success = await safe_remux(job, input_file, output_file)
            
            if success:
                write_trace(job.work_dir, f"[WORKER-ENC-{worker_id}] Encoding success. Routing to Upload Queue.")
                transition_stage(job, Stage.ENCODED)
                await upload_queue.put(job)
            else:
                write_trace(job.work_dir, f"[WORKER-ENC-{worker_id}] ❌ Encoding failed.")
                transition_stage(job, Stage.FAILED)
                
        except Exception as e:
            write_trace(job.work_dir, f"[WORKER-ENC-{worker_id}] Critical unhandled worker crash: {e}")
            transition_stage(job, Stage.FAILED)
            
        finally:
            encode_queue.task_done()
