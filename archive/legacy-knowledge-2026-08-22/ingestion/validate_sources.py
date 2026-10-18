import json
from pathlib import Path

REQUIRED_KEYS = {
    "source_id",
    "name",
    "type",
    "url",
    "jurisdiction",
    "effective_date",
    "retrieval_date",
    "checksum",
    "description",
    "license"
}

VALID_TYPES = {
    "GOVERNMENT",
    "INTERNATIONAL_ORGANIZATION",
    "RESEARCH_INSTITUTION",
    "UNIVERSITY"
}

def validate_source(file_path: Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        
        missing_keys = REQUIRED_KEYS - set(data.keys())
        if missing_keys:
            return False, f"Missing required keys: {', '.join(missing_keys)}"
            
        if data["type"] not in VALID_TYPES:
            return False, f"Invalid source type: {data['type']}. Must be one of {VALID_TYPES}"
            
        return True, "Valid"

def main():
    base_dir = Path(__file__).parent.parent
    registry_dir = base_dir / "source-registry"
    
    if not registry_dir.exists():
        print(f"Registry directory not found at {registry_dir}")
        return
        
    json_files = list(registry_dir.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in {registry_dir}")
        return
        
    all_valid = True
    for json_file in json_files:
        is_valid, message = validate_source(json_file)
        if not is_valid:
            print(f"[FAIL] {json_file.name}: {message}")
            all_valid = False
        else:
            print(f"[PASS] {json_file.name}")
            
    if not all_valid:
        print("\nValidation failed for one or more sources.")
        exit(1)
    else:
        print("\nAll sources validated successfully.")

if __name__ == "__main__":
    main()
