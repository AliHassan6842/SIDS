import httpx
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

class PunjabAgClient:
    """Client for safe HTTP fetching of Punjab Agriculture data."""
    
    def __init__(self, timeout: int = 30, retries: int = 3):
        self.timeout = timeout
        self.retries = retries
        self.headers = {
            "User-Agent": "SIDS_AI/1.0 (Agriculture Knowledge Retrieval; +https://example.com/bot)"
        }
        
    def fetch_page(self, url: str) -> Optional[str]:
        """Safely fetch HTML or JSON with retries, respecting timeouts and boundaries."""
        for attempt in range(self.retries):
            try:
                with httpx.Client(timeout=self.timeout, headers=self.headers, verify=True) as client:
                    response = client.get(url)
                    response.raise_for_status()
                    
                    # Bound response size to prevent massive downloads (e.g., 5MB limit)
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > 5 * 1024 * 1024:
                        logger.warning(f"Response too large: {content_length} bytes from {url}")
                        return None
                        
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' not in content_type and 'application/json' not in content_type:
                        logger.warning(f"Unexpected content type from {url}: {content_type}")
                        # Depending on requirements, we might reject or just warn
                        
                    return response.text
            except httpx.HTTPError as e:
                logger.warning(f"Fetch failed on attempt {attempt + 1} for {url}: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
