from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import hashlib

class ScoutingGuidance(BaseModel):
    guidance_id: str
    
    crop_id: str
    problem_id: Optional[str] = None
    
    sampling_unit: Optional[str] = None
    observation_method: Optional[str] = None
    
    frequency: Optional[str] = None
    season: Optional[str] = None
    distribution_guidance: Optional[str] = None
    
    source_id: str
    source_url: Optional[str] = None
    
    retrieved_at: datetime
    source_checksum: str
    parser_version: str
    review_status: str

class ScoutingParser:
    """Parses raw HTML/JSON into ScoutingGuidance records."""
    
    def __init__(self, parser_version: str = "1.0.0"):
        self.parser_version = parser_version
        
    def parse(self, raw_content: str, source_url: str, retrieved_at: datetime) -> List[ScoutingGuidance]:
        records = []
        source_checksum = hashlib.sha256(raw_content.encode('utf-8')).hexdigest()
        
        # Mock logic
        if "cotton" in raw_content.lower() and "scout" in raw_content.lower():
            records.append(ScoutingGuidance(
                guidance_id="punjab-cotton-scouting-001",
                crop_id="cotton",
                problem_id=None,
                sampling_unit="25 plants per field",
                observation_method="Zig-zag walking pattern",
                frequency="Twice a week",
                season="Kharif",
                distribution_guidance="Randomly select plants from different parts of the field",
                source_id="punjab_ag_ext",
                source_url=source_url,
                retrieved_at=retrieved_at,
                source_checksum=source_checksum,
                parser_version=self.parser_version,
                review_status="AUTO_EXTRACTED"
            ))
            
        return records
