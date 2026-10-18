from bs4 import BeautifulSoup
from typing import List
from knowledge.schemas import IPMManagementOption
from datetime import datetime
import hashlib

class FAONormalizer:
    """Parses HTML or JSON from FAO and normalizes into Pydantic schemas."""
    
    @staticmethod
    def generate_checksum(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
        
    def parse_ipm_evidence(self, html_content: bytes, source_url: str) -> List[IPMManagementOption]:
        """
        Parses IPM evidence HTML into IPMManagementOption objects.
        This is a template that would be adjusted based on actual HTML structure of FAO.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        options = []
        checksum = self.generate_checksum(html_content)
        retrieved_at = datetime.utcnow()
        
        # Example logic for parsing an HTML list
        container = soup.find('div', {'class': 'ipm-options'})
        if not container:
            return options
            
        items = container.find_all('div', {'class': 'ipm-item'})
        for item in items:
            category_elem = item.find('span', {'class': 'category'})
            desc_elem = item.find('p', {'class': 'description'})
            if category_elem and desc_elem:
                opt = IPMManagementOption(
                    category=category_elem.get_text(strip=True).upper(),
                    description=desc_elem.get_text(strip=True),
                    target_problems=[], # extract as appropriate
                    target_crops=[], # extract as appropriate
                    source_id="fao_ipm_evidence",
                    source_url=source_url,
                    retrieved_at=retrieved_at,
                    checksum=checksum
                )
                options.append(opt)
                
        return options
