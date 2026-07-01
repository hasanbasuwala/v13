# core/state/models.py
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Job:
    job_id: str
    url: str
    title: str = "Unknown Job"
    display_title: str = ""
    tags: list = field(default_factory=list)
    work_dir: Path = None
    # (Keep any other fields you currently have)