import asyncio
import logging

from pyrogram.errors import FloodWait

from core.state.queues import queues
from core.state.registry import registry
from core.state.models import JobStage


logger = logging.getLogger(__name__)


async def safe_upload(app, job):

    for attempt in range(5):

        try:

            await app.send_video(

                chat_id=job.user_id,

                video=str(
                    job.output_file
                )
            )

            return True

        except FloodWait as e:

            logger.warning(
                f"Flood wait {e.value}"
            )

            await asyncio.sleep(
                e.value
            )

        except Exception:

            await asyncio.sleep(10)

    return False


async def upload_worker(app):

    logger.info("Upload worker started")

    while True:

        job = await queues.upload_queue.get()

        try:

            await registry.update_stage(
                job.job_id,
                JobStage.UPLOADING
            )

            success = await safe_upload(
                app,
                job
            )

            if not success:

                raise Exception(
                    "Upload failed"
                )

            await registry.update_stage(
                job.job_id,
                JobStage.COMPLETED
            )

            logger.info(
                f"Upload complete {job.job_id}"
            )

        except Exception as e:

            logger.exception(
                f"Upload failed {job.job_id}"
            )

            await registry.set_error(
                job.job_id,
                str(e)
            )

            await registry.update_stage(
                job.job_id,
                JobStage.FAILED
            )

        finally:

            queues.upload_queue.task_done()