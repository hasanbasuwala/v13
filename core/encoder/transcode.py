# core/encoder/transcode.py
import asyncio
import subprocess
from pathlib import Path
from core.state.models import Job
from core.state.persistence import write_trace

async def safe_remux(job: Job, input_file: Path, output_file: Path) -> bool:
    """Safely remuxes the media for Telegram compatibility (faststart, standard AAC)."""
    write_trace(job.work_dir, "[ENCODER] Spawning FFmpeg remux sandbox...")
    
    cmd = [
        "ffmpeg", "-y", "-nostdin", "-i", str(input_file),
        "-c:v", "copy", "-c:a", "aac", "-movflags", "+faststart",
        str(output_file)
    ]
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=asyncio.subprocess.PIPE
        )
        
        _, stderr = await proc.communicate()
        
        if proc.returncode == 0 and output_file.exists():
            write_trace(job.work_dir, "[ENCODER] ✅ FFmpeg remux completed successfully.")
            return True
        else:
            err = stderr.decode('utf-8', errors='ignore').strip()
            write_trace(job.work_dir, f"[ENCODER] ❌ FFmpeg failed with code {proc.returncode}: {err}")
            return False
            
    except Exception as e:
        write_trace(job.work_dir, f"[ENCODER] ❌ FFmpeg execution crashed: {e}")
        return False
