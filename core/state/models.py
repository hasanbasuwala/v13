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
    stage: Stage = Stage.QUEUED
    work_dir: Path = None
