import logging
from typing import List
from .client import DPPClient
from .normalizer import DPPNormalizer
from knowledge.schemas import PesticideRegistration

logger = logging.getLogger(__name__)

class PesticideRegistryAdapter:
    def __init__(self, client: DPPClient, normalizer: DPPNormalizer):
        self.client = client
        self.normalizer = normalizer
        
    def fetch_all(self) -> List[PesticideRegistration]:
        path = "/pesticide-registration"  # Mock path, adapt to reality
        logger.info(f"Fetching pesticide registry from {path}")
        content = self.client.fetch_page(path)
        if not content:
            logger.warning("Failed to fetch pesticide registry.")
            return []
            
        url = f"{self.client.base_url.rstrip('/')}/{path.lstrip('/')}"
        registrations = self.normalizer.parse_pesticide_registry(content, url)
        logger.info(f"Parsed {len(registrations)} pesticide registrations.")
        return registrations
