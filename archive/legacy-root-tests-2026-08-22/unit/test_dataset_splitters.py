import sys
from pathlib import Path

# Fix sys.path for testing
base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(base_dir))

from ml.scripts.split.create_deterministic_splits import deterministic_split


def test_deterministic_split():
    data = [f"item_{i}" for i in range(100)]
    result = deterministic_split(data, seed=42)
    
    assert len(result["train"]) == 80
    assert len(result["val"]) == 10
    assert len(result["test"]) == 10
    
    # Check deterministic behavior
    data2 = [f"item_{i}" for i in range(100)]
    result2 = deterministic_split(data2, seed=42)
    
    assert result["train"] == result2["train"]
    assert result["val"] == result2["val"]
    assert result["test"] == result2["test"]
