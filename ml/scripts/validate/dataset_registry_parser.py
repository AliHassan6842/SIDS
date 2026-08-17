import json
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ValidationError, Field

class DatasetRecord(BaseModel):
    dataset_id: str
    dataset_name: str
    source: str
    source_url: str
    version: str
    license: str
    commercial_use: bool
    redistribution_allowed: bool
    download_date: Optional[str] = None
    checksum: Optional[str] = None
    geography: str
    field_or_lab: str
    crop: str
    problem_types: List[str]
    classes: List[str]
    annotation_type: str
    image_count: int
    bounding_box_count: int = 0
    segmentation_available: bool = False
    known_limitations: List[str] = Field(default_factory=list)
    approved_for_training: bool

class DatasetRegistryParser:
    def __init__(self):
        self.datasets: List[DatasetRecord] = []
        self.malformed_entries: List[Dict[str, Any]] = []

    def load_registry(self, file_path: str) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Registry file not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            raise ValueError("Registry should be a JSON array of dataset entries")
            
        for entry in data:
            self._validate_and_add_entry(entry)

    def _validate_and_add_entry(self, entry: Dict[str, Any]) -> None:
        try:
            record = DatasetRecord(**entry)
            self.datasets.append(record)
        except ValidationError as e:
            self.malformed_entries.append({"entry": entry, "errors": e.errors()})

    def get_valid_datasets(self) -> List[DatasetRecord]:
        return self.datasets

    def get_malformed_entries(self) -> List[Dict[str, Any]]:
        return self.malformed_entries

    def query_by_crop(self, crop: str) -> List[DatasetRecord]:
        return [ds for ds in self.datasets if ds.crop.upper() == crop.upper()]

    def query_by_task(self, task: str) -> List[DatasetRecord]:
        # Task usually maps to problem_types (e.g. 'PEST', 'DISEASE')
        return [ds for ds in self.datasets if task.upper() in (pt.upper() for pt in ds.problem_types)]

    def query_classes(self, target_class: str) -> List[DatasetRecord]:
        return [ds for ds in self.datasets if target_class.lower() in (c.lower() for c in ds.classes)]
