from curl_cffi import requests
from stem import Signal
from stem.control import Controller
import time
from typing import Optional, Dict, Any

class HttpClient:
    def __init__(self, use_tor: bool = True):
        self.use_tor = use_tor
        self.tor_controller = self._setup_tor() if use_tor else None
        self.last_request_time = 0
        self.min_request_interval = 2
        self.requests_before_rotate = 25  # New: rotate IP every N requests
        self.request_count = 0  # New: track request count

        # Standard headers for browser impersonation
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }

    def _setup_tor(self) -> Optional[Controller]:
        try:
            controller = Controller.from_port(port=9051)
            controller.authenticate()
            return controller
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            print(f"Failed to setup Tor: {e}")
            return None

    def _get_tor_proxy(self) -> Dict[str, str]:
        return {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }

    def new_tor_identity(self):
        """Request new Tor identity"""
        if self.tor_controller:
            self.tor_controller.signal(Signal.NEWNYM)
            time.sleep(5)  # Wait for new identity to be ready

    def request(self, method: str, url: str, headers: Dict = None, **kwargs) -> requests.Response:
        """Make HTTP request with curl_cffi, rate limiting and proxy handling"""
        # Rotate Tor identity if needed
        if self.use_tor and self.request_count >= self.requests_before_rotate:
            self.new_tor_identity()
            self.request_count = 0

        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        # if time_since_last < self.min_request_interval:
            # time.sleep(self.min_request_interval - time_since_last)

        # Merge headers with defaults
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)

        # Add Tor proxy if enabled
        if self.use_tor:
            kwargs['proxies'] = self._get_tor_proxy()

        # Make request with curl_cffi
        response = requests.request(
            method,
            url,
            headers=request_headers,
            impersonate="chrome120",  # Use curl_cffi's browser impersonation
            **kwargs
        )

        self.last_request_time = time.time()
        self.request_count += 1  # New: increment request counter

        return response

    def get(self, url: str, **kwargs) -> requests.Response:
        """Convenience method for GET requests"""
        return self.request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Convenience method for POST requests"""
        return self.request('POST', url, **kwargs)
