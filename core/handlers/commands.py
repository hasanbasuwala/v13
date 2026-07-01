# Inside core/handlers/commands.py
import json # Add this import at the top

    @app.on_message(filters.text & filters.user(config.OWNER_ID) & ~filters.command(["start", "dashboard", "update", "stop", "resume", "log"]))
    async def native_link_catcher(client: Client, msg: Message):
        """Catches URLs, extracts captions, and generates the Job Card."""
        url = next((w for w in msg.text.split() if w.startswith("http") or w.startswith("magnet:?")), None)
        if not url:
            return

        # Extract everything that IS NOT the URL to use as the title/caption
        raw_caption = msg.text.replace(url, "").strip()
        
        job_id = f"JOB_{uuid.uuid4().hex[:8].upper()}"
        job_title = raw_caption if raw_caption else job_id
        
        work_dir = config.JOBS_DIR / job_id
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Save title to disk so the Dashboard can read it on reboot
        meta_file = work_dir / "meta.json"
        meta_file.write_text(json.dumps({"title": job_title}))
        
        # Send the initial Job Card
        sent_msg = await msg.reply(
            f"📺 **{job_title}**\n"
            f"🔗 `{url}`\n\n"
            f"🔄 **Status:** Queued 💤"
        )
        
        # Build the Job payload
        job = Job(
            job_id=job_id,
            url=url,
            quality="720", 
            source="telegram",
            work_dir=work_dir,
            title=job_title,          # Inject caption
            ui_chat_id=sent_msg.chat.id,  # Inject tracking ID
            ui_msg_id=sent_msg.id         # Inject tracking ID
        )
        
        transition_stage(job, Stage.QUEUED)
        await download_queue.put(job)
