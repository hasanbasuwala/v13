# core/ui/dashboard.py
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.state.registry import Global_Registry

def build_dashboard_text() -> str:
    """Generates the Mainframe Dashboard text by safely reading the Global Registry."""
    # Access the active jobs dictionary directly from our robust registry instance
    active_jobs = Global_Registry.active_jobs
    
    # Calculate stats dynamically
    stats = {
        "queued": 0, "downloading": 0, "encoding": 0, 
        "uploading": 0, "failed": 0, "done": 0
    }
    
    for job_id, job_data in active_jobs.items():
        stage = job_data.get("stage", "queued")
        if stage in stats:
            stats[stage] += 1

    text = (
        f"╔════════════════════════════════════════╗\n"
        f"║ 📡 SYSTEM_MAINFRAME v13.1              ║\n"
        f"╠════════════════════════════════════════╝\n"
        f"║ [ ⏳ ] QUEUED:       {stats['queued']}\n"
        f"║ [ 📥 ] DOWNLOADING:  {stats['downloading']}\n"
        f"║ [ 🎬 ] ENCODING:     {stats['encoding']}\n"
        f"║ [ 🚀 ] UPLOADING:    {stats['uploading']}\n"
        f"╠════════════════════════════════════════╗\n"
        f"║ ⚠️ FAILED: {stats['failed']}  |  ✅ DONE: {stats['done']}\n"
        f"╚════════════════════════════════════════╝"
    )
    return text

def build_dashboard_kb() -> InlineKeyboardMarkup:
    """Generates the routing keyboard for the dashboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📥 DL", callback_data="filter|downloading"),
            InlineKeyboardButton("🎬 ENC", callback_data="filter|encoding"),
            InlineKeyboardButton("🚀 UP", callback_data="filter|uploading")
        ],
        [
            InlineKeyboardButton("🔄 REFRESH", callback_data="dash_action|refresh"),
            InlineKeyboardButton("☢️ NUKE CACHE", callback_data="dash_action|nuke")
        ]
    ])
