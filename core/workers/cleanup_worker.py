import shutil


async def cleanup(job):

    if job.work_dir.exists():

        shutil.rmtree(
            job.work_dir,
            ignore_errors=True
        )