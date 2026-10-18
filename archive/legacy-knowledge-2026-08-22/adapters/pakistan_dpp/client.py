import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DPPClient:
    """Client for safely fetching from Pakistan Department of Plant Protection."""
    
    def __init__(self, base_url: str = "http://plantprotection.gov.pk", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {
            "User-Agent": "SIDS-Knowledge-Bot/1.0",
            "Accept": "text/html,application/json,application/xhtml+xml"
        }
        
    def fetch_page(self, path: str) -> Optional[bytes]:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                # Bound the response size to avoid huge downloads (e.g., max 10 MB)
                if int(response.headers.get("content-length", 0)) > 10 * 1024 * 1024:
                    logger.warning(f"Response too large for {url}")
                    return None
                return response.content
        except httpx.HTTPError as e:
            logger.error(f"HTTP Error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None
