# core/downloader/engines/aria2.py
import asyncio
from pathlib import Path
from core.state.models import Job
from core.state.persistence import write_trace
from core.security.headers import generate_headers

async def download_direct(job: Job) -> bool:
    """Executes a high-speed parallel download using aria2c."""
    write_trace(job.work_dir, "[ARIA2] Spawning direct download engine...")
    
    # Generate organic headers to bypass basic static file host blocks
    headers = generate_headers()
    user_agent = headers.get("User-Agent", "")
    
    # We don't know the exact extension yet, but we will name the target file safely
    out_file = f"{job.job_id}.media"
    
    # Build the aria2c command for aggressive, parallel chunking
    cmd = [
        "aria2c",
        "--dir", str(job.work_dir),
        "--out", out_file,
        "--split=16",
        "--max-connection-per-server=16",
        "--min-split-size=1M",
        "--summary-interval=0",
        "--file-allocation=none",
        f"--header=User-Agent: {user_agent}",
        job.url
    ]
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            # Rename .media to actual extension based on MIME or fallback to .mp4
            downloaded = job.work_dir / out_file
            if downloaded.exists():
                final_path = job.work_dir / f"{job.job_id}.mp4"
                downloaded.rename(final_path)
                write_trace(job.work_dir, f"[ARIA2] Download complete: {final_path.name}")
                return True
        else:
            err_msg = stderr.decode('utf-8', errors='ignore').strip()
            write_trace(job.work_dir, f"[ARIA2] Process failed with code {proc.returncode}: {err_msg}")
            return False
            
    except Exception as e:
        write_trace(job.work_dir, f"[ARIA2] Execution crashed: {str(e)}")
        return False
        
    return False
