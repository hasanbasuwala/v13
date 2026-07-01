import asyncio
import logging
from pathlib import Path

from core.state.queues import queues
from core.state.registry import registry
from core.state.models import JobStage


logger = logging.getLogger(__name__)


async def run_ffmpeg(input_file, output_file):

    process = await asyncio.create_subprocess_exec(

        "ffmpeg",
        "-y",
        "-i",
        str(input_file),

        "-c:v",
        "libx264",

        str(output_file),

        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    await process.communicate()

    return process.returncode == 0


async def encode_worker(app):

    logger.info("Encode worker started")

    while True:

        job = await queues.encode_queue.get()

        try:

            await registry.update_stage(
                job.job_id,
                JobStage.ENCODING
            )

            input_file = job.work_dir / "input.mp4"

            output_file = (
                job.work_dir /
                f"{job.job_id}_encoded.mp4"
            )

            success = await run_ffmpeg(
                input_file,
                output_file
            )

            if not success:

                raise Exception(
                    "Encoding failed"
                )

            job.output_file = output_file

            await registry.set_output_file(
                job.job_id,
                output_file
            )

            await registry.update_stage(
                job.job_id,
                JobStage.ENCODED
            )

            logger.info(
                f"Encode complete {job.job_id}"
            )

            # send to uploader
            await queues.enqueue_upload(job)

        except Exception as e:

            logger.exception(
                f"Encoding failed {job.job_id}"
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

            queues.encode_queue.task_done()