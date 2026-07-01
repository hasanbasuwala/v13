# test_downloader.py
import asyncio
import shutil
import config
from core.state.models import Job
from core.downloader.manager import process_download

async def run_all_scenarios():
    print("🚀 Initiating Comprehensive Downloader Engine Test...")

    # Define our test scenarios
    scenarios = [
        {
            "id": "SCENARIO_YTDLP",
            "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "desc": "YouTube Video (Tests yt-dlp impersonation)"
        },
        {
            "id": "SCENARIO_ARIA2",
            "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/720/Big_Buck_Bunny_720_10s_1MB.mp4",
            "desc": "Direct MP4 Link (Tests aria2c parallel engine)"
        },
        {
            "id": "SCENARIO_FALLBACK",
            "url": "https://httpbin.org/status/404",
            "desc": "Dead Link (Tests waterfall failure logic)"
        }
    ]

    for data in scenarios:
        job_id = data["id"]
        work_dir = config.JOBS_DIR / job_id
        
        # Clean up past runs
        if work_dir.exists():
            shutil.rmtree(work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)

        test_job = Job(
            job_id=job_id,
            url=data["url"],
            quality="720", 
            source="test_script",
            work_dir=work_dir
        )

        print(f"\n{'='*50}")
        print(f"🎬 Running Scenario: {data['desc']}")
        print(f"🔗 Target URL: {test_job.url}")
        
        # Run the manager
        success = await process_download(test_job)

        if success:
            print("✅ Manager reported SUCCESS!")
            files = [f for f in work_dir.glob("*.*") if f.is_file() and f.suffix not in ['.json', '.log']]
            if files:
                size_mb = files[0].stat().st_size / (1024 * 1024)
                print(f"✅ Verified on disk: {files[0].name} ({size_mb:.2f} MB)")
            else:
                print("❌ Success reported, but no file found on disk.")
        else:
            print("❌ Manager reported FAILURE (Expected for dead links).")

        # Print the trace log
        trace_file = work_dir / "trace.log"
        if trace_file.exists():
            print(f"\n--- 📄 Trace Log for {job_id} ---")
            print(trace_file.read_text(encoding="utf-8").strip())
            print("-" * 34)

if __name__ == "__main__":
    asyncio.run(run_all_scenarios())
