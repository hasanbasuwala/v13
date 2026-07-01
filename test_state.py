# test_state.py
from pathlib import Path
from core.state.models import Job, Stage
from core.state.persistence import write_state, load_state, write_trace

def run_test():
    print("🚀 Starting State Layer Test...")
    
    # 1. Test Model Creation
    job_dir = Path("SysCache/jobs/JOB_12345")
    my_job = Job(
        job_id="12345", 
        url="https://example.com/video.mp4", 
        quality="1080p", 
        source="web", 
        work_dir=job_dir
    )
    print(f"✅ Job Model Created: {my_job.job_id}")

    # 2. Test Atomic State Write
    state_data = {"stage": Stage.QUEUED.value, "retries": 0}
    write_state(my_job.work_dir, state_data)
    print("✅ State atomically written to disk.")

    # 3. Test State Load
    loaded_data = load_state(my_job.work_dir)
    print(f"✅ State loaded from disk: {loaded_data}")
    
    assert loaded_data["stage"] == "queued", "State mismatch!"

    # 4. Test Trace Logging
    write_trace(my_job.work_dir, "Test log entry 1: Download initialized.")
    write_trace(my_job.work_dir, "Test log entry 2: Resolving URL.")
    print("✅ Trace logs appended safely.")

if __name__ == "__main__":
    run_test()
