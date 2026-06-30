# core/downloader/strategy.py
from core.state.models import Job
from core.downloader.engines import ytdlp, aria2, mediago, browser

# Map the string names from pipeline/retry.py to actual async functions
ENGINE_MAP = {
    "yt_dlp_primary": ytdlp.download_primary,
    "yt_dlp_alt": ytdlp.download_alt,
    "aria2_direct": aria2.download_direct,
    "mediago_engine": mediago.download_mediago,
    "playwright_browser": browser.download_interception,
}

async def execute_strategy(strategy_name: str, job: Job) -> bool:
    """Dynamically routes the job to the correct pluggable download engine."""
    engine_func = ENGINE_MAP.get(strategy_name)
    if not engine_func:
        raise ValueError(f"Unknown download strategy mapped: {strategy_name}")
    
    return await engine_func(job)
