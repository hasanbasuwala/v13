import logging

from core.state.queues import queues
from core.state.registry import registry
from core.state.models import JobStage

from core.uploader.telegram import (
    TelegramUploader
)


logger = logging.getLogger(__name__)


async def upload_worker(app):

    while True:

        job = await queues.upload_queue.get()

        try:

            await registry.update_stage(
                job.job_id,
                JobStage.UPLOADING
            )

            success = await (
                TelegramUploader.upload(
                    app,
                    job
                )
            )

            if not success:

                raise Exception(
                    "Upload failed"
                )

            await registry.update_stage(
                job.job_id,
                JobStage.COMPLETED
            )

        except Exception as e:

            logger.exception(e)

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