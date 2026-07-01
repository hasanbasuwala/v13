# core/state/models.py
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

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
    title: str = "Untitled"
    display_title: str = "Untitled" # Added this missing field
    tags: List[str] = field(default_factory=list)
