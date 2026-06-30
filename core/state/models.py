# core/state/models.py
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class Stage(Enum):
    QUEUED = "queued"
    RESOLVING = "resolving"
    DOWNLOADING = "downloading"
    ENCODING = "encoding"
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
