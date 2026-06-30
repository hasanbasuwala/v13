# core/pipeline/retry.py

# Structural strategy map tracking the fallback sequence per classification type
DOWNLOAD_STRATEGIES = {
    "youtube": ["yt_dlp_primary", "yt_dlp_alt", "playwright_browser", "pipeline_failure"],
    "hls": ["mediago_engine", "yt_dlp_alt", "playwright_browser", "pipeline_failure"],
    "direct": ["aria2_direct", "yt_dlp_primary", "playwright_browser", "pipeline_failure"],
    "webpage": ["primp_scraper", "playwright_browser", "yt_dlp_primary", "pipeline_failure"],
    "telegram": ["telegram_native", "pipeline_failure"]
}

def get_strategy(classification: str, attempt: int) -> str:
    """
    Returns the specific download strategy variant based on the current execution attempt.
    The 'attempt' variable is 1-indexed (1, 2, 3...).
    """
    plan = DOWNLOAD_STRATEGIES.get(classification, DOWNLOAD_STRATEGIES["webpage"])
    
    # Map attempt index safely. If attempts exceed plan array size, lock to final item (failure)
    index = min(attempt - 1, len(plan) - 1)
    return plan[index]
