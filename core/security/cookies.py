# core/security/cookies.py
import json
from pathlib import Path
from typing import Dict, Any
import config

COOKIES_DIR = config.BASE_DIR / "cookies"
COOKIES_DIR.mkdir(parents=True, exist_ok=True)

def load_domain_cookies(domain: str) -> Dict[str, str]:
    """Loads localized domain cookies securely from disk storage."""
    cookie_file = COOKIES_DIR / f"{domain}.json"
    if not cookie_file.exists():
        return {}
    try:
        return json.loads(cookie_file.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_domain_cookies(domain: str, cookie_data: Dict[str, Any]) -> None:
    """Atomically commits updated tracking cookies back to disk footprint."""
    from core.state.persistence import _atomic_write
    cookie_file = COOKIES_DIR / f"{domain}.json"
    _atomic_write(cookie_file, json.dumps(cookie_data, indent=2))
