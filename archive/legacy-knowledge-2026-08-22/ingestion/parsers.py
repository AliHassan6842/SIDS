import re
from typing import Dict, Any, List

def check_domain_allowlist(url: str, allowed_domains: List[str]) -> bool:
    """Checks if a given URL belongs to the allowed domains."""
    from urllib.parse import urlparse
    try:
        domain = urlparse(url).netloc
        for allowed in allowed_domains:
            if domain == allowed or domain.endswith('.' + allowed):
                return True
        return False
    except Exception:
        return False


def parse_punjab_thresholds(raw_text: str) -> List[Dict[str, Any]]:
    """
    Parses Punjab economic thresholds from raw text.
    Mock implementation for testing parsing logic of gold sets.
    Expected format in raw text: "Pest: <name>, Threshold: <value> <unit>"
    """
    results = []
    # simple mock regex for testing
    pattern = r"Pest:\s*(?P<pest>[^,]+),\s*Threshold:\s*(?P<value>\d+)\s*(?P<unit>[^\n]+)"
    
    for match in re.finditer(pattern, raw_text, re.IGNORECASE):
        results.append({
            "pest": match.group("pest").strip(),
            "threshold_value": int(match.group("value").strip()),
            "unit": match.group("unit").strip()
        })
    return results


def parse_dpp_fao_data(raw_data: dict) -> List[Dict[str, Any]]:
    """
    Parses DPP (Department of Plant Protection) / FAO data into a structured format.
    Mock implementation for testing.
    """
    results = []
    items = raw_data.get("items", [])
    for item in items:
        if "guideline" in item and "chemical" in item:
            results.append({
                "chemical": item["chemical"],
                "guideline": item["guideline"],
                "source": item.get("source", "UNKNOWN")
            })
    return results
