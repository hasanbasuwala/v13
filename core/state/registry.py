import asyncio
from datetime import datetime
from typing import Dict, Optional, List

from core.state.models import Job, JobStage


class JobRegistry:
    """
    Central async-safe in-memory registry.

    Used by:
        download_worker
        encode_worker
        upload_worker
        telegram handlers
        status monitor
    """

    def __init__(self):

        # active jobs indexed by job_id
        self._jobs: Dict[str, Job] = {}

        # async safety lock
        self._lock = asyncio.Lock()

    async def add_job(self, job: Job):

        async with self._lock:
            self._jobs[job.job_id] = job

    async def get_job(self, job_id: str) -> Optional[Job]:

        async with self._lock:
            return self._jobs.get(job_id)

    async def update_stage(
        self,
        job_id: str,
        stage: JobStage
    ):

        async with self._lock:

            job = self._jobs.get(job_id)

            if not job:
                return False

            job.stage = stage

            return True

    async def set_output_file(
        self,
        job_id: str,
        output_path
    ):

        async with self._lock:

            job = self._jobs.get(job_id)

            if not job:
                return False

            job.output_file = output_path

            return True

    async def set_thumbnail(
        self,
        job_id: str,
        thumbnail_path
    ):

        async with self._lock:

            job = self._jobs.get(job_id)

            if not job:
                return False

            job.thumbnail_file = thumbnail_path

            return True

    async def increment_retry(
        self,
        job_id: str
    ):

        async with self._lock:

            job = self._jobs.get(job_id)

            if not job:
                return False

            job.retries += 1

            return True

    async def set_error(
        self,
        job_id: str,
        error_message: str
    ):

        async with self._lock:

            job = self._jobs.get(job_id)

            if not job:
                return False

            job.last_error = str(error_message)

            return True

    async def request_cancel(
        self,
        job_id: str
    ):

        async with self._lock:

            job = self._jobs.get(job_id)

            if not job:
                return False

            job.cancel_requested = True

            job.stage = JobStage.CANCELLED

            return True

    async def remove_job(
        self,
        job_id: str
    ):

        async with self._lock:

            self._jobs.pop(job_id, None)

    async def list_jobs(self) -> List[Job]:

        async with self._lock:

            return list(self._jobs.values())

    async def cleanup_finished(self):

        """
        Remove completed jobs older than 30 min
        """

        async with self._lock:

            remove_list = []

            now = datetime.utcnow()

            for job_id, job in self._jobs.items():

                if job.stage in [
                    JobStage.COMPLETED,
                    JobStage.FAILED,
                    JobStage.CANCELLED
                ]:

                    age = (
                        now - job.created_at
                    ).total_seconds()

                    if age > 1800:
                        remove_list.append(job_id)

            for job_id in remove_list:
                del self._jobs[job_id]


registry = JobRegistry()