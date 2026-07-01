# core/uploader/metadata.py
import asyncio
import json
from pathlib import Path

async def extract_video_metadata(file_path: Path):
    """Uses ffprobe to extract exact video dimensions and duration for Telegram."""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(file_path)
    ]
    
    try:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        
        data = json.loads(stdout)
        width = height = duration = 0
        
        if 'format' in data and 'duration' in data['format']:
            duration = int(float(data['format']['duration']))
            
        for stream in data.get('streams', []):
            if stream['codec_type'] == 'video':
                width = int(stream.get('width', 0))
                height = int(stream.get('height', 0))
                break
                
        return width, height, duration
    except Exception:
        # Fallback to zeros if extraction fails; Telegram will attempt to guess
        return 0, 0, 0