# core/state/models.py
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class Stage(Enum):
    QUEUED = "queued"
    RESOLVING = "resolving"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"   # <-- Added for Encode Queue waiting
    ENCODING = "encoding"
    ENCODED = "encoded"         # <-- Added for Upload Queue waiting
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
