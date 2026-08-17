import sys
from pathlib import Path

import cv2
import numpy as np

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from ml.scripts.validate.dataset_qa_pipeline import dataset_qa_check


def test_dataset_qa_check(tmp_path):
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()
    
    img_dir = dataset_dir / "images"
    img_dir.mkdir()
    
    # 1 valid image
    img1 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    cv2.imwrite(str(img_dir / "valid1.jpg"), img1)
    
    # 1 duplicate of valid1
    cv2.imwrite(str(img_dir / "valid1_dup.jpg"), img1)
    
    # 1 corrupt image
    with open(img_dir / "corrupt.jpg", "wb") as f:
        f.write(b"not an image")
        
    dataset_qa_check(str(dataset_dir))
    
    reports_dir = tmp_path / "reports"
    report_file = reports_dir / f"qa_report_{dataset_dir.name}.txt"
    
    assert report_file.exists()
    content = report_file.read_text()
    
    assert "Corrupt:" in content
    assert "corrupt.jpg" in content
    assert "Duplicates:" in content
    assert "valid1_dup.jpg" in content
