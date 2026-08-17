import os
import json
import pytest
import tempfile
from ml.scripts.validate.dataset_registry_parser import DatasetRegistryParser, DatasetRecord

@pytest.fixture
def sample_registry_data():
    return [
        {
            "dataset_id": "ip102-cotton-subset",
            "dataset_name": "IP102 Cotton Subset",
            "source": "IP102",
            "source_url": "https://github.com/IP102",
            "version": "1.0",
            "license": "CC BY-NC 4.0",
            "commercial_use": False,
            "redistribution_allowed": True,
            "download_date": "2026-08-01",
            "geography": "Global",
            "field_or_lab": "FIELD",
            "crop": "COTTON",
            "problem_types": ["PEST"],
            "classes": ["cotton-whitefly", "cotton-jassid"],
            "annotation_type": "CLASSIFICATION",
            "image_count": 1500,
            "approved_for_training": True
        },
        {
            "dataset_id": "plantvillage-tomato",
            "dataset_name": "PlantVillage Tomato",
            "source": "PlantVillage",
            "source_url": "https://plantvillage.psu.edu/",
            "version": "1.0",
            "license": "CC0",
            "commercial_use": True,
            "redistribution_allowed": True,
            "download_date": "2026-08-01",
            "geography": "Global",
            "field_or_lab": "LAB",
            "crop": "TOMATO",
            "problem_types": ["DISEASE"],
            "classes": ["tomato-early-blight", "HEALTHY"],
            "annotation_type": "CLASSIFICATION",
            "image_count": 5000,
            "approved_for_training": True
        },
        {
            # Malformed entry (missing required field: crop)
            "dataset_id": "bad-dataset",
            "dataset_name": "Bad Dataset",
            "source": "Unknown",
            "source_url": "http://example.com",
            "version": "0.1",
            "license": "None",
            "commercial_use": False,
            "redistribution_allowed": False,
            "geography": "Unknown",
            "field_or_lab": "UNKNOWN",
            "problem_types": ["PEST"],
            "classes": ["unknown-pest"],
            "annotation_type": "BBOX",
            "image_count": 10,
            "approved_for_training": False
        }
    ]

@pytest.fixture
def temp_registry_file(sample_registry_data):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, 'w') as f:
        json.dump(sample_registry_data, f)
    yield path
    os.remove(path)

def test_load_registry_and_validation(temp_registry_file):
    parser = DatasetRegistryParser()
    parser.load_registry(temp_registry_file)
    
    valid_datasets = parser.get_valid_datasets()
    assert len(valid_datasets) == 2
    assert isinstance(valid_datasets[0], DatasetRecord)
    assert valid_datasets[0].dataset_id == "ip102-cotton-subset"
    
    malformed = parser.get_malformed_entries()
    assert len(malformed) == 1
    assert malformed[0]["entry"]["dataset_id"] == "bad-dataset"

def test_query_by_crop(temp_registry_file):
    parser = DatasetRegistryParser()
    parser.load_registry(temp_registry_file)
    
    cotton_datasets = parser.query_by_crop("COTTON")
    assert len(cotton_datasets) == 1
    assert cotton_datasets[0].crop == "COTTON"
    
    rice_datasets = parser.query_by_crop("RICE")
    assert len(rice_datasets) == 0

def test_query_by_task(temp_registry_file):
    parser = DatasetRegistryParser()
    parser.load_registry(temp_registry_file)
    
    disease_datasets = parser.query_by_task("DISEASE")
    assert len(disease_datasets) == 1
    assert disease_datasets[0].dataset_id == "plantvillage-tomato"

def test_query_classes(temp_registry_file):
    parser = DatasetRegistryParser()
    parser.load_registry(temp_registry_file)
    
    whitefly_ds = parser.query_classes("cotton-whitefly")
    assert len(whitefly_ds) == 1
    assert "cotton-whitefly" in whitefly_ds[0].classes

def test_invalid_json_format():
    parser = DatasetRegistryParser()
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, 'w') as f:
        # Not a list
        json.dump({"dataset_id": "test"}, f)
    
    with pytest.raises(ValueError, match="Registry should be a JSON array"):
        parser.load_registry(path)
        
    os.remove(path)
