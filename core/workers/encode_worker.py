import logging

from core.state.queues import queues
from core.state.registry import registry
from core.state.models import JobStage

from core.encoder.ffmpeg import FFmpegEncoder
from core.encoder.thumbnail import ThumbnailGenerator


logger = logging.getLogger(__name__)


async def encode_worker(app):

    while True:

        job = await queues.encode_queue.get()

        try:

            await registry.update_stage(
                job.job_id,
                JobStage.ENCODING
            )

            input_file = (
                job.work_dir /
                "input.mp4"
            )

            output_file = (
                job.work_dir /
                "encoded.mp4"
            )

            thumb_file = (
                job.work_dir /
                "thumb.jpg"
            )

            await FFmpegEncoder.encode(
                input_file,
                output_file
            )

            await ThumbnailGenerator.generate(
                output_file,
                thumb_file
            )

            job.output_file = output_file

            job.thumbnail_file = thumb_file

            await registry.set_output_file(
                job.job_id,
                output_file
            )

            await registry.set_thumbnail(
                job.job_id,
                thumb_file
            )

            await registry.update_stage(
                job.job_id,
                JobStage.ENCODED
            )

            await queues.enqueue_upload(
                job
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

            queues.encode_queue.task_done()