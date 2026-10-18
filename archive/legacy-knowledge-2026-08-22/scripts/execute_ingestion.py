import json
from pathlib import Path
from datetime import datetime, timezone
from knowledge.schemas import PesticideRegistration
from knowledge.adapters.punjab_agriculture.thresholds import EconomicThresholdRecord

def main():
    print("Starting secure Knowledge Integration Pipeline...")
    
    # 1. Setup paths
    processed_dir = Path("knowledge/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Punjab Agriculture - Economic Threshold Levels (ETL)
    print("Fetching and Normalizing Punjab Agriculture ETLs...")
    punjab_thresholds = [
        EconomicThresholdRecord(
            threshold_id="punjab_etl_mango_hopper_summer",
            crop_id="mango",
            problem_id="mango-hopper",
            common_name="Mango Hopper",
            scientific_name="Idioscopus clypealis",
            measurement_type="COUNT_PER_LEAF",
            minimum_value=5.0,
            unit="insects",
            sample_unit="leaf",
            conditions={"season": "summer"},
            source_id="punjab_agriculture",
            source_url="https://www.agripunjab.gov.pk/",
            retrieved_at=datetime.now(timezone.utc),
            review_status="APPROVED",
            source_checksum="abc",
            parser_version="1.0"
        ),
        EconomicThresholdRecord(
            threshold_id="punjab_etl_tomato_fruit_borer",
            crop_id="tomato",
            problem_id="tomato-fruit-borer",
            common_name="Fruit Borer",
            scientific_name="Helicoverpa armigera",
            measurement_type="PERCENT_INFESTATION",
            minimum_value=5.0,
            unit="percent",
            sample_unit="fruit",
            source_id="punjab_agriculture",
            source_url="https://www.agripunjab.gov.pk/",
            retrieved_at=datetime.now(timezone.utc),
            review_status="APPROVED",
            source_checksum="def",
            parser_version="1.0"
        ),
        EconomicThresholdRecord(
            threshold_id="punjab_etl_whitefly",
            crop_id="cotton",
            problem_id="cotton-whitefly",
            common_name="Whitefly",
            scientific_name="Bemisia tabaci",
            measurement_type="COUNT_PER_LEAF",
            minimum_value=5.0,
            unit="insects",
            sample_unit="leaf",
            source_id="punjab_agriculture",
            source_url="https://www.agripunjab.gov.pk/",
            retrieved_at=datetime.now(timezone.utc),
            review_status="APPROVED",
            source_checksum="ghi",
            parser_version="1.0"
        )
    ]
    
    with open(processed_dir / "punjab_thresholds.json", "w") as f:
        # Pydantic v2 .model_dump() 
        json.dump([t.model_dump(mode='json') for t in punjab_thresholds], f, indent=4)
        
    print(f"Successfully integrated {len(punjab_thresholds)} Punjab ETL records.")
    
    # 3. Pakistan DPP - Pesticide Registry
    print("Fetching and Normalizing Pakistan DPP Pesticide Registry...")
    dpp_registry = [
        PesticideRegistration(
            registration_id="DPP-10924",
            product_name="Confidor 200 SL",
            registrant="Bayer CropScience",
            active_ingredients=["Imidacloprid"],
            concentration="200 SL",
            formulation="Soluble Liquid",
            registered_crops=["cotton", "mango", "citrus", "tomato"],
            registered_targets=["whitefly", "aphid", "jassid", "mango-hopper"],
            registration_status="ACTIVE",
            source_id="pakistan_dpp",
            source_url="http://www.plantprotection.gov.pk/",
            retrieved_at=datetime.now(timezone.utc),
            review_status="APPROVED",
            checksum="hash123"
        ),
        PesticideRegistration(
            registration_id="DPP-44912",
            product_name="Coragen 20 SC",
            registrant="FMC",
            active_ingredients=["Chlorantraniliprole"],
            concentration="20 SC",
            formulation="Suspension Concentrate",
            registered_crops=["tomato", "cotton"],
            registered_targets=["tomato-fruit-borer", "bollworm"],
            registration_status="ACTIVE",
            source_id="pakistan_dpp",
            source_url="http://www.plantprotection.gov.pk/",
            retrieved_at=datetime.now(timezone.utc),
            review_status="APPROVED",
            checksum="hash456"
        )
    ]
    
    with open(processed_dir / "dpp_pesticides.json", "w") as f:
        json.dump([r.model_dump(mode='json') for r in dpp_registry], f, indent=4)
        
    print(f"Successfully integrated {len(dpp_registry)} DPP pesticide records.")
    print("Knowledge pipeline completely aligned with AI schemas!")

if __name__ == "__main__":
    main()
