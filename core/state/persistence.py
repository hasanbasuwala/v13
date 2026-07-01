# core/state/persistence.py
import sys
import json
import asyncio
import traceback
from pathlib import Path
from core.state.registry import Global_Registry

def log_stealth(message: str, new_line: bool = True) -> None:
    """Uses ANSI escape codes to overwrite the previous line or print a new one."""
    if not new_line:
        # \r returns cursor to start of line, \033[K clears to end of line
        sys.stdout.write(f"\r\033[K{message}")
    else:
        sys.stdout.write(f"\n{message}")
    sys.stdout.flush()

def write_trace(work_dir: Path, message: str, exception: Exception = None) -> None:
    """Writes log messages. If an exception is provided, appends the full stack trace."""
    log_file = work_dir / "trace.log"
    with open(log_file, "a") as f:
        f.write(f"{message}\n")
        if exception:
            f.write("--- FULL STACK TRACE ---\n")
            f.write(traceback.format_exc())
            f.write("\n------------------------\n")

async def registry_heartbeat(cache_dir: Path) -> None:
    """Periodically saves the Global_Registry to disk every 60 seconds."""
    registry_file = cache_dir / "registry.json"
    while True:
        try:
            # Grab a snapshot of the current state
            jobs_snapshot = await Global_Registry.get_all_jobs()
            
            # Write safely to disk
            with open(registry_file, "w") as f:
                json.dump(jobs_snapshot, f, indent=4)
                
        except Exception as e:
            log_stealth(f"[⚠️] Heartbeat failed to write registry: {e}", new_line=True)
            
        await asyncio.sleep(60)