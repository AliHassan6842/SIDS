import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


def create_deterministic_split(
    items: list[dict[str, Any]], 
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
    group_key: str = None
) -> dict[str, list[dict[str, Any]]]:
    """
    Creates a deterministic train/val/test split.
    If group_key is provided, items with the same group_key value will be assigned 
    to the same split to avoid data leakage (e.g. same farm, same video, duplicate cluster).
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-6, "Ratios must sum to 1.0"
    
    # Sort items by a unique identifier to ensure deterministic order before shuffling
    # We assume 'id' or 'image_path' exists
    items_sorted = sorted(items, key=lambda x: x.get('id', x.get('image_path', str(x))))
    
    rng = random.Random(seed)
    
    if group_key:
        # Group items
        groups = defaultdict(list)
        for item in items_sorted:
            g_val = item.get(group_key, "UNKNOWN_GROUP")
            groups[g_val].append(item)
            
        group_keys_sorted = sorted(list(groups.keys()))
        rng.shuffle(group_keys_sorted)
        
        train_split = []
        val_split = []
        test_split = []
        
        total_items = len(items_sorted)
        train_target = int(total_items * train_ratio)
        val_target = int(total_items * val_ratio)
        
        for g_val in group_keys_sorted:
            group_items = groups[g_val]
            if len(train_split) < train_target:
                train_split.extend(group_items)
            elif len(val_split) < val_target:
                val_split.extend(group_items)
            else:
                test_split.extend(group_items)
    else:
        # Standard splitting
        rng.shuffle(items_sorted)
        total = len(items_sorted)
        train_idx = int(total * train_ratio)
        val_idx = train_idx + int(total * val_ratio)
        
        train_split = items_sorted[:train_idx]
        val_split = items_sorted[train_idx:val_idx]
        test_split = items_sorted[val_idx:]
        
    return {
        "train": train_split,
        "val": val_split,
        "test": test_split
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a deterministic dataset split.")
    parser.add_argument("--manifest", type=str, required=True, help="Path to JSON manifest of items")
    parser.add_argument("--seed", type=int, default=2026, help="Random seed for deterministic splitting")
    parser.add_argument("--group-by", type=str, default=None, help="Key in JSON to group by (e.g. 'source', 'cluster_id')")
    parser.add_argument("--train", type=float, default=0.8, help="Train ratio")
    parser.add_argument("--val", type=float, default=0.1, help="Val ratio")
    parser.add_argument("--test", type=float, default=0.1, help="Test ratio")
    parser.add_argument("--output", type=str, default="split.json", help="Output file path")
    
    args = parser.parse_args()
    
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Error: Manifest {manifest_path} not found.")
        exit(1)
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        items = json.load(f)
        
    splits = create_deterministic_split(
        items, 
        train_ratio=args.train, 
        val_ratio=args.val, 
        test_ratio=args.test,
        seed=args.seed,
        group_key=args.group_by
    )
    
    # Print summary
    print(f"Total items: {len(items)}")
    print(f"Train: {len(splits['train'])}")
    print(f"Val: {len(splits['val'])}")
    print(f"Test: {len(splits['test'])}")
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)
    print(f"Split written to {args.output}")
