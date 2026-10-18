import logging
from typing import List
from .client import FAOClient
from .normalizer import FAONormalizer
from knowledge.schemas import IPMManagementOption

logger = logging.getLogger(__name__)

class FAOIPMAdapter:
    def __init__(self, client: FAOClient, normalizer: FAONormalizer):
        self.client = client
        self.normalizer = normalizer
        
    def fetch_ipm_evidence(self) -> List[IPMManagementOption]:
        path = "/pest-and-pesticide-management/ipm-evidence"  # Mock path, adapt to reality
        logger.info(f"Fetching FAO IPM evidence from {path}")
        content = self.client.fetch_page(path)
        if not content:
            logger.warning("Failed to fetch FAO IPM evidence.")
            return []
            
        url = f"{self.client.base_url.rstrip('/')}/{path.lstrip('/')}"
        options = self.normalizer.parse_ipm_evidence(content, url)
        logger.info(f"Parsed {len(options)} IPM management options.")
        return options
