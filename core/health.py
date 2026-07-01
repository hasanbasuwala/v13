from core.state.registry import registry


async def health_check():

    jobs = await registry.list_jobs()

    return {

        "active_jobs":
            len(jobs)
    }