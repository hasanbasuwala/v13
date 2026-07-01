# core/handlers/callbacks.py
import shutil
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
import config
from core.ui.dashboard import build_dashboard_text, build_dashboard_kb

def register_callbacks(app: Client):
    """Registers interactive button callbacks with the Pyrogram client."""
    
    @app.on_callback_query(filters.regex(r"^page\|(\d+)"))
    async def cb_pagination(client: Client, query: CallbackQuery):
        """Handles dashboard pagination clicks."""
        if query.from_user.id != config.OWNER_ID:
            return await query.answer("Access Denied", show_alert=True)
            
        page = int(query.matches[0].group(1))
        
        try:
            await query.message.edit_text(
                build_dashboard_text(page=page),
                reply_markup=build_dashboard_kb(page=page)
            )
            await query.answer()
        except Exception:
            # Pyrogram throws an error if we edit the message with the exact same text
            await query.answer("Already on this page.", show_alert=False)

    @app.on_callback_query(filters.regex(r"^ui\|clean"))
    async def cb_clean_cache(client: Client, query: CallbackQuery):
        """Wipes the job cache from the disk."""
        if query.from_user.id != config.OWNER_ID:
            return await query.answer("Access Denied", show_alert=True)
            
        await query.answer("🧹 Nuking cache...", show_alert=False)
        
        # Delete all job folders
        for folder in config.JOBS_DIR.iterdir():
            if folder.is_dir():
                shutil.rmtree(folder, ignore_errors=True)
                
        # Refresh dashboard back to page 0
        await query.message.edit_text(
            build_dashboard_text(page=0),
            reply_markup=build_dashboard_kb(page=0)
        )
        
    @app.on_callback_query(filters.regex(r"^noop$"))
    async def cb_noop(client: Client, query: CallbackQuery):
        """Empty callback for decorative buttons (like page numbers)."""
        await query.answer()