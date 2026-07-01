# core/encoder/detect.py
from pathlib import Path

def needs_remux(file_path: Path) -> bool:
    """Checks if the downloaded file actually needs FFmpeg processing."""
    # If it's already an MP4, bypass the FFmpeg sandbox to save heavy CPU usage
    if file_path.suffix.lower() == '.mp4':
        return False
    return True