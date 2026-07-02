import uuid
from pathlib import Path

from pyrogram import filters
from pyrogram.types import Message

from app import app

from core.state.models import Job, JobStage
from core.state.registry import registry
from core.state.queues import queues


@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):

    await message.reply_text(

        "Bot online.\n"
        "Send a video URL."
    )


@app.on_message(
    filters.text &
    ~filters.command("start")
)
async def url_handler(

    client,

    message: Message
):

    url = message.text.strip()

    job_id = str(

        uuid.uuid4()

    )[:8]

    work_dir = Path(

        f"/tmp/{job_id}"

    )

    work_dir.mkdir(

        parents=True,

        exist_ok=True
    )

    new_job = Job(

        job_id=job_id,

        url=url,

        stage=JobStage.QUEUED,

        user_id=message.chat.id,

        work_dir=work_dir
    )

    await registry.add_job(

        new_job
    )

    await queues.enqueue_download(

        new_job
    )

    await message.reply_text(

        f"Queued job: {job_id}"
    )