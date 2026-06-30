# core/downloader/strategy.py
from core.downloader.engines import ytdlp, aria2, mediago, browser

ENGINE_MAP = {
    "yt_dlp_primary": ytdlp.download_primary,
    "yt_dlp_alt": ytdlp.download_alt,
    "aria2_direct": aria2.download_direct,
    "mediago_engine": mediago.download_mediago,
    "playwright_browser": browser.download_interception,
}
# ... (rest of execute_strategy remains the same)
