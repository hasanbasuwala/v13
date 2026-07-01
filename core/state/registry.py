import asyncio
from typing import Dict
from core.state.models import Job


class JobRegistry:

    def __init__(self):

        self.jobs: Dict[str, Job] = {}

        self.lock = asyncio.Lock()

    async def add_job(self, job: Job):

        async with self.lock:

            self.jobs[job.job_id] = job

    async def get_job(self, job_id):

        async with self.lock:

            return self.jobs.get(job_id)

    async def update_stage(self, job_id, stage):

        async with self.lock:

            if job_id in self.jobs:
                self.jobs[job_id].stage = stage

    async def set_error(self, job_id, error):

        async with self.lock:

            if job_id in self.jobs:
                self.jobs[job_id].last_error = str(error)

    async def remove_job(self, job_id):

        async with self.lock:

            self.jobs.pop(job_id, None)


registry = JobRegistry()