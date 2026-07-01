from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Optional


class JobStage(str, Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    ENCODING = "encoding"
    ENCODED = "encoded"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:

    job_id: str
    url: str

    stage: JobStage = JobStage.QUEUED

    work_dir: Optional[Path] = None

    output_file: Optional[Path] = None
    thumbnail_file: Optional[Path] = None

    retries: int = 0
    last_error: Optional[str] = None

    cancel_requested: bool = False

    created_at: datetime = field(default_factory=datetime.utcnow)

    user_id: Optional[int] = None