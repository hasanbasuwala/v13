# core/state/models.py
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class Stage(Enum):
    QUEUED = "queued"
    RESOLVING = "resolving"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    ENCODING = "encoding"
    ENCODED = "encoded"
    UPLOADING = "uploading"
    DONE = "done"
    FAILED = "failed"

@dataclass
class Job:
    job_id: str
    url: str
    quality: str
    source: str
    work_dir: Path
    title: str = ""          # Stores your custom #caption
    ui_chat_id: int = 0      # Tracks the Telegram Chat ID
    ui_msg_id: int = 0       # Tracks the Job Card Message ID