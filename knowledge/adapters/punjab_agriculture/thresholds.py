from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib

class EconomicThresholdRecord(BaseModel):
    threshold_id: str
    
    crop_id: str
    problem_id: str
    
    common_name: Optional[str] = None
    scientific_name: Optional[str] = None
    
    measurement_type: str  # e.g., COUNT_PER_LEAF, PERCENT_DAMAGE, VISIBLE_DAMAGE
    
    minimum_value: Optional[float] = None
    maximum_value: Optional[float] = None
    
    unit: Optional[str] = None
    sample_unit: Optional[str] = None
    
    season: Optional[str] = None
    month_start: Optional[int] = None
    month_end: Optional[int] = None
    growth_stage: Optional[str] = None
    
    conditions: Dict[str, Any] = Field(default_factory=dict)
    
    source_id: str
    source_url: Optional[str] = None
    
    retrieved_at: datetime
    effective_date: Optional[datetime] = None
    
    source_checksum: str
    parser_version: str
    review_status: str  # e.g., AUTO_EXTRACTED, VALIDATED, REJECTED, NEEDS_REVIEW

class ThresholdParser:
    """Parses raw HTML/JSON into EconomicThresholdRecords."""
    
    def __init__(self, parser_version: str = "1.0.0"):
        self.parser_version = parser_version
        
    def parse(self, raw_content: str, source_url: str, retrieved_at: datetime) -> List[EconomicThresholdRecord]:
        """
        Parses the raw content to extract threshold records.
        In a real scenario, this would use BeautifulSoup to extract rows from the Punjab Pest Warning tables.
        """
        records = []
        source_checksum = hashlib.sha256(raw_content.encode('utf-8')).hexdigest()
        
        # Mocking the extraction logic for demonstration.
        # A real implementation would parse the DOM here.
        if "cotton" in raw_content.lower() and "whitefly" in raw_content.lower():
            records.append(EconomicThresholdRecord(
                threshold_id="punjab-cotton-whitefly-001",
                crop_id="cotton",
                problem_id="cotton-whitefly",
                common_name="Whitefly",
                scientific_name="Bemisia tabaci",
                measurement_type="COUNT_PER_LEAF",
                minimum_value=5.0,
                maximum_value=None,
                unit="adults/nymphs",
                sample_unit="leaf",
                source_id="punjab_pest_warning",
                source_url=source_url,
                retrieved_at=retrieved_at,
                source_checksum=source_checksum,
                parser_version=self.parser_version,
                review_status="AUTO_EXTRACTED"
            ))
            
        if "cotton" in raw_content.lower() and "bollworm" in raw_content.lower():
            records.append(EconomicThresholdRecord(
                threshold_id="punjab-cotton-pbw-001",
                crop_id="cotton",
                problem_id="cotton-pink-bollworm",
                common_name="Pink Bollworm",
                scientific_name="Pectinophora gossypiella",
                measurement_type="PERCENT_DAMAGE",
                minimum_value=5.0,
                maximum_value=None,
                unit="%",
                sample_unit="bolls",
                source_id="punjab_pest_warning",
                source_url=source_url,
                retrieved_at=retrieved_at,
                source_checksum=source_checksum,
                parser_version=self.parser_version,
                review_status="AUTO_EXTRACTED"
            ))
            
        return records
