# core/downloader/engines/aria2.py
import asyncio
from pathlib import Path
from core.state.persistence import write_trace

async def download_direct(job) -> bool:
    """Fallback engine using aria2c for raw links."""
    out_file = job.work_dir / f"{job.job_id}.mp4"
    cmd = [
        "aria2c", 
        "-x", "16", "-s", "16", 
        "-d", str(job.work_dir), 
        "-o", f"{job.job_id}.mp4", 
        job.url
    ]
    
    write_trace(job.work_dir, "[ARIA2] Spawning direct download engine...")
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    
    if proc.returncode == 0:
        return True
    else:
        # Capture the specific error from aria2
        error_msg = stderr.decode().strip()
        write_trace(job.work_dir, f"[ARIA2] Process failed with code {proc.returncode}: {error_msg}")
        return False