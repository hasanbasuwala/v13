# core/pipeline/classifier.py

def classify(url: str) -> str:
    """Parses a target URL and classifies its type to guide the routing engine."""
    url_lower = url.lower()
    
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    
    if ".m3u8" in url_lower:
        return "hls"
        
    if any(ext in url_lower for ext in [".mp4", ".mkv", ".ts", ".mov", ".avi"]):
        return "direct"
        
    if "t.me/" in url_lower or "telegram_bridge" in url_lower:
        return "telegram"
        
    return "webpage"
