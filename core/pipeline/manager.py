from core.state.registry import registry


class Pipeline:

    @staticmethod
    async def transition(job, stage):

        await registry.update_stage(

            job.job_id,

            stage
        )