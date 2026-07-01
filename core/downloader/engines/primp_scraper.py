# core/downloader/engines/primp_scraper.py
import asyncio
import re
import primp
from core.state.models import Job
from core.state.persistence import write_trace

def _run_primp_download(job: Job) -> bool:
    """Synchronous function to execute the TLS spoofed request."""
    # Spoof a modern Chrome browser to bypass Cloudflare
    client = primp.Client(impersonate="chrome_120")
    
    # 1. Request the target webpage
    resp = client.get(job.url)
    if resp.status_code != 200:
        write_trace(job.work_dir, f"[PRIMP] HTTP {resp.status_code} on initial request.")
        return False
        
    # 2. Parse the raw HTML for hidden .mp4 links using regex
    # Looks for anything starting with http and ending with .mp4 inside quotes
    match = re.search(r'["\'](https?://[^"\']+\.mp4[^"\']*)["\']', resp.text)
    
    target_url = job.url
    if match:
        target_url = match.group(1)
        write_trace(job.work_dir, f"[PRIMP] Found hidden media link: {target_url}")
    elif ".mp4" not in job.url:
        write_trace(job.work_dir, "[PRIMP] No media links found in HTML.")
        return False
    
    # 3. Download the actual media file using the spoofed connection
    out_file = job.work_dir / f"{job.job_id}.mp4"
    media_resp = client.get(target_url)
    
    if media_resp.status_code == 200:
        out_file.write_bytes(media_resp.content)
        return True
        
    return False

async def download_primp(job: Job) -> bool:
    """Executes a highly-stealthy Cloudflare bypass to scrape and download media."""
    write_trace(job.work_dir, "[PRIMP] Launching TLS impersonation scraper...")
    
    try:
        # Run the blocking primp network calls in a background thread
        success = await asyncio.to_thread(_run_primp_download, job)
        if success:
            write_trace(job.work_dir, "[PRIMP] ✅ Stealth download completed successfully.")
        else:
            write_trace(job.work_dir, "[PRIMP] ❌ Failed to extract or download media.")
        return success
    except Exception as e:
        write_trace(job.work_dir, f"[PRIMP] Crash: {e}")
        return False