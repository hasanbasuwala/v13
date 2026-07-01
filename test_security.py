# test_security.py
from core.security.fingerprints import get_random_target, get_ytdlp_impersonate_args
from core.security.headers import generate_headers
from core.security.session import create_stealth_session

def run_security_test():
    print("🚀 Initiating Security Layer Verification Block...")

    # 1. Test Fingerprint Generation
    target = get_random_target()
    print(f"✅ Fingerprint Pool Extracted Target Browser: {target['browser']} v{target['version']}")
    
    ytdlp_args = get_ytdlp_impersonate_args()
    print(f"✅ yt-dlp Formatted Impersonation Array: {ytdlp_args}")
    assert len(ytdlp_args) == 2

    # 2. Test Header Alignment
    headers = generate_headers()
    print(f"✅ Headers Successfully Compiled. User-Agent string length: {len(headers['User-Agent'])}")
    assert "User-Agent" in headers

    # 3. Test Active Network Session Creation via curl_cffi
    print("🌐 Launching live test request against encrypted metadata endpoint...")
    try:
        # Utilizing HTTPBin to inspect what our request headers look like to a remote server
        session = create_stealth_session(domain="httpbin")
        response = session.get("https://httpbin.org/headers", timeout=10)
        
        if response.status_code == 200:
            server_received_headers = response.json().get("headers", {})
            print(f"✅ Remote Server Validation Successful (HTTP 200).")
            print(f"   Server read our User-Agent as: {server_received_headers.get('User-Agent')}")
        else:
            print(f"❌ Server rejected request with status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Network test execution crashed: {e}")

if __name__ == "__main__":
    run_security_test()
