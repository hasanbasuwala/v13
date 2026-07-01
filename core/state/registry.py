# core/state/registry.py
import asyncio

class SystemRegistry:
    def __init__(self):
        self.active_jobs = {}
        # Using an asyncio.Lock ensures that simultaneous updates from 
        # different workers don't corrupt the dictionary data.
        self.lock = asyncio.Lock()
        
    async def register_job(self, job_id: str, job_data: dict) -> None:
        async with self.lock:
            self.active_jobs[job_id] = job_data
            
    async def update_job(self, job_id: str, updates: dict) -> None:
        async with self.lock:
            if job_id in self.active_jobs:
                self.active_jobs[job_id].update(updates)
                
    async def get_job(self, job_id: str) -> dict:
        async with self.lock:
            return self.active_jobs.get(job_id)

    async def get_all_jobs(self) -> dict:
        async with self.lock:
            return dict(self.active_jobs)

    async def remove_job(self, job_id: str) -> None:
        async with self.lock:
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]

# Instantiate the single global instance
Global_Registry = SystemRegistry()