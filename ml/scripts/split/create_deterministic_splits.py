import random


def deterministic_split(data_items, seed=42):
    random.seed(seed)
    random.shuffle(data_items)
    n = len(data_items)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)
    
    return {
        "train": data_items[:train_end],
        "val": data_items[train_end:val_end],
        "test": data_items[val_end:]
    }
