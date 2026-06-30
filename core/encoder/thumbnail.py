# core/encoder/thumbnail.py
import asyncio
import subprocess
from pathlib import Path
from core.state.models import Job
from core.state.persistence import write_trace

async def generate_thumbnail(job: Job, input_file: Path, output_file: Path) -> bool:
    """Extracts a thumbnail from the 2-second mark of the video."""
    write_trace(job.work_dir, "[ENCODER] Generating video thumbnail...")
    
    cmd = [
        "ffmpeg", "-y", "-i", str(input_file),
        "-ss", "00:00:02", "-vframes", "1",
        str(output_file)
    ]
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        await proc.wait()
        
        if output_file.exists():
            write_trace(job.work_dir, "[ENCODER] ✅ Thumbnail generated successfully.")
            return True
            
        write_trace(job.work_dir, "[ENCODER] ⚠️ Thumbnail output missing.")
        return False
        
    except Exception as e:
        write_trace(job.work_dir, f"[ENCODER] ⚠️ Thumbnail extraction failed: {e}")
        return False
