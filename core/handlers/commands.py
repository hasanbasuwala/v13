# core/handlers/commands.py
import re
from pyrogram import Client, filters
from core.state.models import Job
from core.state.persistence import log_stealth

@Client.on_message(filters.text & filters.private)
async def process_new_link(client, message):
    raw_text = message.text
    
    # 1. Extract the URL (Basic extraction, adjust to your exact regex if needed)
    url_match = re.search(r'(https?://[^\s]+)', raw_text)
    if not url_match:
        return
    url = url_match.group(0)
    
    # 2. Extract Hashtags
    tags = re.findall(r'#\w+', raw_text)
    
    # 3. Clean the Title (Remove URL and Tags)
    clean_text = raw_text.replace(url, '')
    clean_title = re.sub(r'#\w+', '', clean_text).strip()
    if not clean_title:
        clean_title = "Untitled_Media"

    # 4. Create the Job
    job_id = f"JOB_{message.id}" # Or your custom ID generator
    new_job = Job(
        job_id=job_id,
        url=url,
        title=raw_text, # Keep raw if needed for fallback
        display_title=clean_title,
        tags=tags
    )
    
    # Send quick intake confirmation
    tag_str = " ".join(tags) if tags else "None"
    await message.reply_text(
        f"📥 **Job Queued!**\n"
        f"🆔 `{job_id}`\n"
        f"🏷️ **Tags:** {tag_str}\n"
        f"📺 **Title:** {clean_title}"
    )
    
    log_stealth(f"[INTAKE] {job_id} | Title: {clean_title} | Tags: {len(tags)}", new_line=True)
    
    # (Push new_job to your download_queue here)