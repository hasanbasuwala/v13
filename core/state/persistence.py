# core/state/persistence.py
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

def _atomic_write(file_path: Path, data: str) -> None:
    """Writes data safely using an isolated tempfile swap routine."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=file_path.parent, text=True)
    
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno()) 
        os.replace(temp_name, file_path)
    except Exception as e:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise e

def write_state(job_dir: Path, state_data: Dict[str, Any]) -> None:
    _atomic_write(job_dir / "state.json", json.dumps(state_data, indent=2))

def load_state(job_dir: Path) -> Dict[str, Any]:
    state_file = job_dir / "state.json"
    if not state_file.exists():
        return {}
    return json.loads(state_file.read_text(encoding='utf-8'))

def write_meta(job_dir: Path, meta_data: Dict[str, Any]) -> None:
    _atomic_write(job_dir / "meta.json", json.dumps(meta_data, indent=2))

def write_trace(job_dir: Path, log_msg: str) -> None:
    """Appends messages to tracking log and forces an active disk flush."""
    trace_file = job_dir / "trace.log"
    trace_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(trace_file, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")
        f.flush()
        os.fsync(f.fileno())
