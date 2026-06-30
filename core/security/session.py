# core/security/session.py
from curl_cffi import requests
from core.security.fingerprints import get_random_target
from core.security.headers import generate_headers
from core.security.cookies import load_domain_cookies

def create_stealth_session(domain: str = "generic") -> requests.Session:
    """Spawns an isolated curl_cffi session loaded with dynamic fingerprints."""
    target = get_random_target()
    session = requests.Session(impersonate=target["browser"])
    
    # Inject aligned standard structural header block
    session.headers.update(generate_headers())
    
    # Inject context domain specific saved cookies if available
    cookies = load_domain_cookies(domain)
    if cookies:
        session.cookies.update(cookies)
        
    return session
