# core/downloader/engines/mediago.py
import asyncio
from core.state.models import Job
from core.state.persistence import write_trace

async def download_mediago(job: Job) -> bool:
    """Executes HLS stream extraction using MediaGo."""
    write_trace(job.work_dir, "[MEDIAGO] Spawning HLS engine...")
    
    out_file = job.work_dir / f"{job.job_id}.mp4"
    # MediaGo command with concurrency to handle HLS segment stitching
    cmd = ["mediago", "e", "-u", job.url, "-o", str(out_file), "--concurrency", "32"]
    
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    
    await proc.communicate()
    
    if proc.returncode == 0 and out_file.exists():
        write_trace(job.work_dir, "[MEDIAGO] HLS download complete.")
        return True
    
    write_trace(job.work_dir, "[MEDIAGO] Failed to produce output.")
    return False
