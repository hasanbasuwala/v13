# core/ui/callbacks.py
import shutil
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from core.state.registry import Global_Registry
from core.ui.render import generate_mainframe_dashboard
# Note: Specific worker termination functions will be linked in Phase 3

async def handle_ui_callbacks(app: Client, callback_query: CallbackQuery) -> None:
    data = callback_query.data
    job_id = data.split("|")[1] if "|" in data else None
    
    # --- JOB CARD ACTIONS ---
    if data.startswith("ui_log|"):
        # We will fully link this up with the automated log sender file in phase 3
        await callback_query.answer("Retrieving job log trace...", show_alert=False)
        
    elif data.startswith("ui_cancel|"):
        # Soft stop logic
        await callback_query.answer("Cancelling active execution...", show_alert=True)
        await Global_Registry.update_job(job_id, {"stage": "failed", "progress": 0})
        
    elif data.startswith("ui_delete|"):
        # Hard nuke logic for a single job
        await callback_query.answer("Nuking job workspace...", show_alert=True)
        job_data = await Global_Registry.get_job(job_id)
        if job_data and "work_dir" in job_data:
            try:
                shutil.rmtree(job_data["work_dir"])
            except Exception:
                pass
        await Global_Registry.remove_job(job_id)
        await callback_query.message.edit_text(f"// 🗑️ JOB `{job_id}` DELETED & CLEANED")

    # --- DASHBOARD ACCORDION FILTERS ---
    elif data.startswith("filter|"):
        target_filter = data.split("|")[1]
        all_jobs = await Global_Registry.get_all_jobs()
        
        # Filter jobs based on selected accordion tab
        filtered_jobs = []
        for j_id, j_meta in all_jobs.items():
            if target_filter == "ROOT" or j_meta.get("stage") == target_filter:
                filtered_jobs.append({"id": j_id, "progress": j_meta.get("progress", 0)})
        
        # Build placeholder statistics for system render
        stats = {"downloading": 0, "waiting_proc": 0, "processing": 0, "waiting_up": 0, "uploading": 0, "disk_usage": "Calculating..."}
        for j_meta in all_jobs.values():
            stage = j_meta.get("stage")
            if stage in stats:
                stats[stage] += 1
                
        text, markup = generate_mainframe_dashboard(stats, filtered_jobs, current_filter=target_filter)
        await callback_query.message.edit_text(text, reply_markup=markup)
        await callback_query.answer()