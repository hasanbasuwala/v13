# core/workers/encode_worker.py
import asyncio
import shutil
from core.state.queues import encode_queue, upload_queue
from core.state.models import Job, Stage
from core.state.persistence import write_trace
from core.pipeline.manager import transition_stage
from core.encoder.transcode import safe_remux
from core.encoder.thumbnail import generate_thumbnail
from core.encoder.detect import needs_remux

# Import commands to access the BOT_PAUSED flag
from core.handlers import commands

async def encode_worker(worker_id: int) -> None:
    """Background worker that smartly processes or bypasses FFmpeg."""
    print(f"🎬 Encode Worker {worker_id} online...")
    
    while True:
        # Respect the /stop command
        if commands.BOT_PAUSED:
            await asyncio.sleep(2)
            continue
            
        job: Job = await encode_queue.get()
        transition_stage(job, Stage.ENCODING)
        
        try:
            dl_files = [f for f in job.work_dir.glob("*.*") if f.is_file() and f.suffix not in ['.json', '.log', '.part']]
            if not dl_files:
                raise FileNotFoundError("No media file found.")
                
            input_file = max(dl_files, key=lambda p: p.stat().st_size)
            output_file = job.work_dir / f"{job.job_id}_enc.mp4"
            thumb_file = job.work_dir / f"{job.job_id}_thumb.jpg"
            
            await generate_thumbnail(job, input_file, thumb_file)
            
            if not needs_remux(input_file):
                write_trace(job.work_dir, "[ENCODER] ⚡ File is already MP4. Bypassing FFmpeg remux.")
                shutil.move(str(input_file), str(output_file))
                success = True
            else:
                success = await safe_remux(job, input_file, output_file)
            
            if success:
                transition_stage(job, Stage.ENCODED)
                await upload_queue.put(job)
            else:
                transition_stage(job, Stage.FAILED)
                
        except Exception as e:
            write_trace(job.work_dir, f"[WORKER-ENC] Crash: {e}")
            transition_stage(job, Stage.FAILED)
        finally:
            encode_queue.task_done()