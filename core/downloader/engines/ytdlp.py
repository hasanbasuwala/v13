# core/downloader/engines/ytdlp.py
import asyncio
from yt_dlp import YoutubeDL
from yt_dlp.networking.impersonate import ImpersonateTarget
from core.state.models import Job
from core.state.persistence import write_trace
from core.security.fingerprints import get_random_target
from core.security.headers import generate_headers

async def download_primary(job: Job) -> bool:
    """Executes a standard yt-dlp extraction with dynamic security injection."""
    write_trace(job.work_dir, "[YT-DLP] Spawning primary engine...")
    
    # 1. Security Injection
    target = get_random_target()
    headers = generate_headers()
    
    # Clean the quality variable to match yt-dlp sorting
    fmt = 'bestvideo+bestaudio/best' if job.quality == 'best' else f'bestvideo[height<={job.quality}]+bestaudio/best[height<={job.quality}]'
    
    # FIX: Wrap the fingerprint in the ImpersonateTarget object required by the Python API
    client_str = f"{target['browser']}:{target['version']}"
    impersonate_obj = ImpersonateTarget(client=client_str, os=target['os'])
    
    ydl_opts = {
        'outtmpl': str(job.work_dir / f"{job.job_id}.%(ext)s"),
        'format': fmt,
        'quiet': True,
        'no_warnings': True,
        'http_headers': headers,
        'impersonate': impersonate_obj
    }
    
    # 2. Execute blocking call safely inside an async executor thread
    loop = asyncio.get_running_loop()
    
    def _extract():
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([job.url])
            
    await loop.run_in_executor(None, _extract)
    return True

async def download_alt(job: Job) -> bool:
    """Alternative yt-dlp fallback (e.g., using different extractors or bypassing auth)."""
    write_trace(job.work_dir, "[YT-DLP] Spawning alternative fallback engine...")
    # Intentionally raising an error to demonstrate how the Manager catches it 
    # and automatically falls back to Attempt 3 in the waterfall.
    raise NotImplementedError("Alternative strategy intentionally failed for waterfall testing.")
