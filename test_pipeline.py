# test_pipeline.py
import asyncio
from pathlib import Path
import config
from core.state.models import Job, Stage
from core.state.queues import download_queue
from core.pipeline.classifier import classify
from core.pipeline.retry import get_strategy
from core.pipeline.scheduler import queue_for_download
from core.pipeline.manager import transition_stage

async def run_pipeline_test():
    print("🚀 Starting Pipeline Layer Routing Test...")
    
    # 1. Test URL Classification
    urls_to_test = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://example.com/live/stream.m3u8",
        "https://storage.cdn.com/file.mp4"
    ]
    
    expected_classes = ["youtube", "hls", "direct"]
    for url, expected in zip(urls_to_test, expected_classes):
        actual = classify(url)
        print(f"✅ Classify '{url[:30]}...' -> Got: {actual}")
        assert actual == expected, f"Classification failure! Got {actual}, expected {expected}"

    # 2. Test Cascade Strategy Engine
    print("🔄 Testing Strategy Cascade (Fallback Waterfall):")
    for attempt in [1, 2, 3, 4]:
        strategy = get_strategy("youtube", attempt)
        print(f"   Attempt {attempt} Strategy -> {strategy}")
    
    assert get_strategy("youtube", 1) == "yt_dlp_primary"
    assert get_strategy("youtube", 4) == "pipeline_failure"

    # 3. Test Integrated Scheduling Lifecycle
    test_job = Job(
        job_id="PIPE_999",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        quality="1080p",
        source="test",
        work_dir=config.JOBS_DIR / "PIPE_999"
    )
    
    # Transition stage via Manager
    transition_stage(test_job, Stage.RESOLVING)
    
    # Queue job via Scheduler
    await queue_for_download(test_job)
    
    # Verify job safely landed inside the State Queue
    assert download_queue.qsize() == 1, "Scheduler failed to populate download queue!"
    fetched_job = await download_queue.get()
    print(f"✅ Scheduler safely popped Job {fetched_job.job_id} out of memory Queue.")
    print("🎉 Pipeline Routing verification completely successful!")

if __name__ == "__main__":
    asyncio.run(run_pipeline_test())
