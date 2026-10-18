from bs4 import BeautifulSoup
from typing import List, Dict, Any
from knowledge.schemas import PesticideRegistration
from datetime import datetime
import hashlib

class DPPNormalizer:
    """Parses HTML or JSON from DPP and normalizes into Pydantic schemas."""
    
    @staticmethod
    def generate_checksum(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
        
    def parse_pesticide_registry(self, html_content: bytes, source_url: str) -> List[PesticideRegistration]:
        """
        Parses pesticide registry HTML into PesticideRegistration objects.
        This is a template that would be adjusted based on actual HTML structure of DPP.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        registrations = []
        checksum = self.generate_checksum(html_content)
        retrieved_at = datetime.utcnow()
        
        # Example logic for parsing an HTML table
        table = soup.find('table', {'id': 'registry_table'})
        if not table:
            return registrations
            
        rows = table.find_all('tr')
        for row in rows[1:]: # Skip header
            cols = row.find_all('td')
            if len(cols) >= 5:
                reg = PesticideRegistration(
                    product_name=cols[0].get_text(strip=True),
                    active_ingredients=[cols[1].get_text(strip=True)],
                    registrant=cols[2].get_text(strip=True),
                    registered_crops=[c.strip() for c in cols[3].get_text(strip=True).split(',')],
                    registration_status=cols[4].get_text(strip=True),
                    source_id="pakistan_dpp_registry",
                    source_url=source_url,
                    retrieved_at=retrieved_at,
                    checksum=checksum
                )
                registrations.append(reg)
                
        return registrations
