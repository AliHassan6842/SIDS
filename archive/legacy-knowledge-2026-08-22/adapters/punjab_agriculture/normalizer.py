from typing import List, Dict, Any
from datetime import datetime, timezone
import logging
from .client import PunjabAgClient
from .thresholds import ThresholdParser, EconomicThresholdRecord
from .scouting import ScoutingParser, ScoutingGuidance

logger = logging.getLogger(__name__)

class PunjabAgNormalizer:
    """Orchestrates fetching, parsing, and normalizing of Punjab Agriculture data."""
    
    def __init__(self):
        self.client = PunjabAgClient()
        self.threshold_parser = ThresholdParser()
        self.scouting_parser = ScoutingParser()
        
    def ingest_thresholds(self, url: str) -> List[EconomicThresholdRecord]:
        """Fetches and normalizes threshold data from a given URL."""
        logger.info(f"Ingesting Punjab thresholds from {url}")
        
        # 1. Fetch
        raw_content = self.client.fetch_page(url)
        if not raw_content:
            logger.warning(f"Failed to fetch content from {url}")
            return []
            
        retrieved_at = datetime.now(timezone.utc)
        
        # 2. Parse & Normalize
        records = self.threshold_parser.parse(
            raw_content=raw_content,
            source_url=url,
            retrieved_at=retrieved_at
        )
        
        logger.info(f"Extracted {len(records)} threshold records.")
        return records
        
    def ingest_scouting(self, url: str) -> List[ScoutingGuidance]:
        """Fetches and normalizes scouting guidance data from a given URL."""
        logger.info(f"Ingesting Punjab scouting guidance from {url}")
        
        # 1. Fetch
        raw_content = self.client.fetch_page(url)
        if not raw_content:
            logger.warning(f"Failed to fetch content from {url}")
            return []
            
        retrieved_at = datetime.now(timezone.utc)
        
        # 2. Parse & Normalize
        records = self.scouting_parser.parse(
            raw_content=raw_content,
            source_url=url,
            retrieved_at=retrieved_at
        )
        
        logger.info(f"Extracted {len(records)} scouting records.")
        return records
