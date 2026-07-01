import logging

from core.state.queues import queues
from core.state.registry import registry
from core.state.models import JobStage

from core.downloader.manager import DownloaderManager


logger = logging.getLogger(__name__)


async def download_worker(app):

    logger.info("Download worker started")

    while True:

        job = await queues.download_queue.get()

        try:

            logger.info(
                f"Downloading job {job.job_id}"
            )

            await registry.update_stage(
                job.job_id,
                JobStage.DOWNLOADING
            )

            success = await DownloaderManager.download(job)

            if not success:

                raise Exception(
                    "Download failed"
                )

            await registry.update_stage(
                job.job_id,
                JobStage.DOWNLOADED
            )

            logger.info(
                f"Download completed {job.job_id}"
            )

            # send to encoder
            await queues.enqueue_encode(job)

        except Exception as e:

            logger.exception(
                f"Download failed {job.job_id}"
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

            queues.download_queue.task_done()