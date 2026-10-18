import logging
from typing import Dict, Any
from .client import DPPClient

logger = logging.getLogger(__name__)

class PesticideLawsAdapter:
    def __init__(self, client: DPPClient):
        self.client = client
        
    def fetch_laws(self) -> Dict[str, Any]:
        path = "/pesticide-rules-and-ordinance"
        logger.info(f"Fetching pesticide laws from {path}")
        content = self.client.fetch_page(path)
        if not content:
            logger.warning("Failed to fetch pesticide laws.")
            return {}
            
        return {
            "source_url": f"{self.client.base_url.rstrip('/')}/{path.lstrip('/')}",
            "raw_content": content,
            "status": "success"
        }
