# core/handlers/commands.py
import uuid
import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message
import config
from core.ui.dashboard import build_dashboard_text, build_dashboard_kb

def register_commands(app: Client):
    """Registers basic text and command handlers with the Pyrogram client."""
    
    @app.on_message(filters.command(["start", "dashboard"]) & filters.user(config.OWNER_ID))
    async def init_dashboard(client: Client, msg: Message):
        """Spawns the main pinned dashboard."""
        await msg.reply(
            build_dashboard_text(page=0),
            reply_markup=build_dashboard_kb(page=0)
        )

    @app.on_message(filters.text & filters.user(config.OWNER_ID) & ~filters.command(["start", "dashboard"]))
    async def native_link_catcher(client: Client, msg: Message):
        """Catches raw URLs pasted in chat and prompts for quality selection."""
        url = next((w for w in msg.text.split() if w.startswith("http") or w.startswith("magnet:?")), None)
        if not url:
            return

        title_hint = msg.text.replace(url, "").strip() or urllib.parse.urlparse(url).netloc or url[:40]
        
        # We will wire this to a confirm card shortly, but for now, let's acknowledge it:
        await msg.reply(f"🔗 **URL Caught!**\n`{url}`\n\n*(Callback routing will be connected in the next step to queue this!)*")