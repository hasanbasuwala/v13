# core/pipeline/manager.py
from core.state.models import Job, Stage
from core.state.persistence import write_state, write_trace

def transition_stage(job: Job, target_stage: Stage) -> None:
    """Enforces atomic state modification during critical step transitions."""
    state_update = {
        "job_id": job.job_id,
        "url": job.url,
        "stage": target_stage.value
    }
    write_state(job.work_dir, state_update)
    write_trace(job.work_dir, f"[PIPELINE-MANAGER] Advanced state to: {target_stage.value}")
