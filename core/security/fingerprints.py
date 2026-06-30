# core/security/fingerprints.py
import random
from typing import Dict, Any

# Supported impersonation configurations for curl_cffi and yt_dlp
IMPERSONATION_POOL = [
    {"browser": "chrome", "version": "110", "os": "windows"},
    {"browser": "chrome", "version": "120", "os": "windows"},
    {"browser": "edge", "version": "115", "os": "windows"},
    {"browser": "safari", "version": "17_0", "os": "ios"}
]

def get_random_target() -> Dict[str, str]:
    """Selects a random browser impersonation profile from the validated pool."""
    return random.choice(IMPERSONATION_POOL)

def get_ytdlp_impersonate_args() -> list:
    """Formats impersonation parameters directly for consumption by yt-dlp."""
    target = get_random_target()
    # maps to yt-dlp's internal --impersonate format
    client = f"{target['browser']}:{target['version']}"
    return ["--impersonate", client]
