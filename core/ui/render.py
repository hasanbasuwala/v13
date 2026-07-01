# core/ui/render.py
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.state.models import Job

def generate_job_card(job: Job, progress: float, stage: str, speed: str = "N/A") -> tuple[str, InlineKeyboardMarkup]:
    """Generates a Style 2 Digital Minimalist Job Card and its action buttons."""
    # Build text representation
    filled = int(progress / 10)
    bar = "|" * filled + "-" * (10 - filled)
    
    text = (
        f"// 🆔 `{job.job_id}`\n"
        f"// 📺 {job.title}\n"
        f"------------------------------------------\n"
        f"STATUS:   {stage.upper()}\n"
        f"PROGRESS: [{bar}] {int(progress)}%\n"
        f"THROUGH:  {speed}\n"
        f"------------------------------------------"
    )
    
    # Inline buttons tied to specific job actions
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📄 LOGS", callback_data=f"ui_log|{job.job_id}"),
            InlineKeyboardButton("❌ CANCEL", callback_data=f"ui_cancel|{job.job_id}"),
            InlineKeyboardButton("🗑️ DELETE", callback_data=f"ui_delete|{job.job_id}")
        ]
    ])
    return text, markup

def generate_mainframe_dashboard(stats: dict, active_jobs: list = None, current_filter: str = "ROOT") -> tuple[str, InlineKeyboardMarkup]:
    """Generates the Mainframe Dashboard text and Accordion layouts based on filters."""
    
    if current_filter == "ROOT":
        text = (
            f"╔════════════════════════════════════════╗\n"
            f"║ 📡 SYSTEM_MAINFRAME v13.1              ║\n"
            f"╠════════════════════════════════════════╝\n"
            f"║ [ 📥 ] DOWNLOADING: {stats.get('downloading', 0)}\n"
            f"║ [ ⏳ ] WAITING_PROC: {stats.get('waiting_proc', 0)}\n"
            f"║ [ 🎬 ] PROCESSING:   {stats.get('processing', 0)}\n"
            f"║ [ 📤 ] WAITING_UP:   {stats.get('waiting_up', 0)}\n"
            f"║ [ 🚀 ] UPLOADING:    {stats.get('uploading', 0)}\n"
            f"╠════════════════════════════════════════╗\n"
            f"║ 💾 STORAGE_MONITOR: {stats.get('disk_usage', 'N/A')}\n"
        )
        if active_jobs:
            for idx, job in enumerate(active_jobs[:5], 1):
                text += f"║ {idx}. {job['id']} - [ {job['progress']}% ]\n"
        text += "╚════════════════════════════════════════╝"
        
        # Dashboard Root Buttons
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📥 DL", callback_data="filter|downloading"),
                InlineKeyboardButton("⏳ WAIT", callback_data="filter|waiting_proc"),
                InlineKeyboardButton("🎬 PROC", callback_data="filter|processing")
            ],
            [
                InlineKeyboardButton("📤 WAIT_UP", callback_data="filter|waiting_up"),
                InlineKeyboardButton("🚀 UP", callback_data="filter|uploading")
            ],
            [
                InlineKeyboardButton("🔄 REFRESH", callback_data="dash_action|refresh"),
                InlineKeyboardButton("🗄️ STORAGE_MGR", callback_data="dash_action|storage")
            ],
            [
                InlineKeyboardButton("☢️ NUKE CACHE", callback_data="dash_action|nuke"),
                InlineKeyboardButton("⚙️ ENGINE LOG", callback_data="dash_action|enginelog")
            ]
        ])
        
    else:
        # Expanded Accordion Filter View
        text = (
            f"╔════════════════════════════════════════╗\n"
            f"║ 📡 {current_filter.upper()} ({len(active_jobs)} ACTIVE)\n"
            f"╠════════════════════════════════════════╝\n"
        )
        if not active_jobs:
            text += "║  No active jobs in this phase.\n"
        for idx, job in enumerate(active_jobs, 1):
            filled = int(job['progress'] / 10)
            bar = "▰" * filled + "▱" * (10 - filled)
            text += f"║ {idx}. `{job['id']}`\n║    {bar} {job['progress']}%\n"
        text += "╠════════════════════════════════════════╗\n╚════════════════════════════════════════╝"
        
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ BACK TO DASHBOARD", callback_data="filter|ROOT")]
        ])
        
    return text, markup