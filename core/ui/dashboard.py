# core/ui/dashboard.py
import json
from pathlib import Path
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config
from core.state.registry import live_progress
from core.state.queues import encode_queue, upload_queue

JOBS_PER_PAGE = 4

def make_bar(percent: float, width: int = 8) -> str:
    """Generates a text-based progress bar."""
    filled = int(max(0.0, min(percent, 100.0)) / (100.0 / width))
    return "█" * filled + "░" * (width - filled)

def _all_job_folders() -> list[Path]:
    if not config.JOBS_DIR.exists():
        return []
    return sorted(
        [d for d in config.JOBS_DIR.iterdir() if d.is_dir() and d.name.startswith("JOB_") or d.name.startswith("PIPE_") or True],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

def build_dashboard_text(page: int = 0) -> str:
    """Generates the dynamic dashboard text."""
    active_count = len(live_progress)
    wait_enc = encode_queue.qsize()
    wait_up = upload_queue.qsize()
    
    # Storage calculation
    storage_mb = sum(f.stat().st_size for f in config.JOBS_DIR.rglob("*") if f.is_file()) / (1024 ** 2)

    sys_status = "🟢 Idle" if active_count == 0 and wait_enc == 0 and wait_up == 0 else f"🔵 Busy  ({active_count} active)"

    # Active Jobs section
    active_lines = ""
    for jid, data in list(live_progress.items()):
        stage = data.get("stage", "Working")
        pct = data.get("pct", 0.0)
        title = data.get("title", jid)[:22]
        bar = make_bar(pct)
        active_lines += f"  `{title}`\n  `[{bar}]` {pct:.1f}%  _{stage}_\n"
    if not active_lines:
        active_lines = "  _Nothing running_\n"

    # Paginated Job List
    all_folders = _all_job_folders()
    total_jobs = len(all_folders)
    total_pages = max(1, (total_jobs + JOBS_PER_PAGE - 1) // JOBS_PER_PAGE)
    safe_page = max(0, min(page, total_pages - 1))

    page_slice = all_folders[safe_page * JOBS_PER_PAGE : (safe_page + 1) * JOBS_PER_PAGE]
    job_lines = ""
    for folder in page_slice:
        jid = folder.name
        title = jid[:8]
        stage = "?"
        
        meta_f = folder / "meta.json"
        state_f = folder / "state.json"
        
        if meta_f.exists():
            try:
                title = json.loads(meta_f.read_text()).get("title", jid)[:28]
            except Exception: pass
        if state_f.exists():
            try:
                stage = json.loads(state_f.read_text()).get("stage", "?")
            except Exception: pass
            
        job_lines += f"  • `{title}`  _{stage}_\n"
    if not job_lines:
        job_lines = "  _No jobs on disk_\n"

    return (
        f"🖥  **STEALTH BOT DASHBOARD**\n"
        f"{'─' * 30}\n\n"
        f"**Status**\n{sys_status}\n\n"
        f"**Active  ({active_count})**\n{active_lines}\n"
        f"**Queued**\n  Wait Encode: `{wait_enc}`\n  Wait Upload: `{wait_up}`\n\n"
        f"**All Jobs** (page {safe_page + 1}/{total_pages})\n{job_lines}\n"
        f"**Storage** `{storage_mb:.1f} MB`"
    )

def build_dashboard_kb(page: int = 0) -> InlineKeyboardMarkup:
    """Generates the inline keyboard for the dashboard."""
    all_folders = _all_job_folders()
    total_pages = max(1, (len(all_folders) + JOBS_PER_PAGE - 1) // JOBS_PER_PAGE)
    safe_page = max(0, min(page, total_pages - 1))

    prev_btn = InlineKeyboardButton("◀ Prev", callback_data=f"page|{safe_page - 1}") if safe_page > 0 else InlineKeyboardButton("·", callback_data="noop")
    next_btn = InlineKeyboardButton("Next ▶", callback_data=f"page|{safe_page + 1}") if safe_page < total_pages - 1 else InlineKeyboardButton("·", callback_data="noop")

    return InlineKeyboardMarkup([
        [prev_btn, InlineKeyboardButton(f"{safe_page + 1}/{total_pages}", callback_data="noop"), next_btn],
        [
            InlineKeyboardButton("📥 New Download", callback_data="ui|download"),
            InlineKeyboardButton("🧹 Nuke Cache", callback_data="ui|clean"),
        ]
    ])
