import os
import shutil
import random
from pathlib import Path

def physical_split(src_dir, dest_dir, train_ratio=0.8):
    src = Path(src_dir)
    dest = Path(dest_dir)
    
    train_dir = dest / "train"
    val_dir = dest / "val"
    
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)
    
    classes = [d for d in src.iterdir() if d.is_dir()]
    
    for cls in classes:
        cls_name = cls.name
        (train_dir / cls_name).mkdir(exist_ok=True)
        (val_dir / cls_name).mkdir(exist_ok=True)
        
        images = list(cls.glob("*.jpg")) + list(cls.glob("*.JPG")) + list(cls.glob("*.png"))
        random.shuffle(images)
        
        train_count = int(len(images) * train_ratio)
        train_imgs = images[:train_count]
        val_imgs = images[train_count:]
        
        for img in train_imgs:
            shutil.copy2(img, train_dir / cls_name / img.name)
            
        for img in val_imgs:
            shutil.copy2(img, val_dir / cls_name / img.name)
            
        print(f"{cls_name}: {len(train_imgs)} train, {len(val_imgs)} val")

if __name__ == "__main__":
    random.seed(42)
    # Just do a tiny subset for PlantVillage so it doesn't take 5 minutes to copy
    physical_split("ml/datasets/plantvillage/PlantVillage", "ml/datasets/plantvillage/split")
