from pathlib import Path

import cv2
import numpy as np


def dataset_qa_check(directory: str):
    p = Path(directory)
    if not p.exists():
        return
        
    images = list(p.glob("**/*.jpg")) + list(p.glob("**/*.png"))
    hashes = {}
    duplicates = []
    corrupt = []
    
    print(f"Starting QA on {len(images)} images in {directory}")
    
    for img_path in images:
        # Check corrupt
        img = cv2.imread(str(img_path))
        if img is None:
            corrupt.append(str(img_path))
            continue
            
        # Check duplicate via phash (using simple block mean here for no dependencies)
        resized = cv2.resize(img, (8, 8), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        mean_val = np.mean(gray)
        phash = "".join(["1" if pixel > mean_val else "0" for pixel in gray.flatten()])
        
        if phash in hashes:
            duplicates.append((str(img_path), hashes[phash]))
        else:
            hashes[phash] = str(img_path)
            
    print("QA Results:")
    print(f"Corrupt images: {len(corrupt)}")
    print(f"Near/Exact duplicates: {len(duplicates)}")
    
    # Actually log them to a report
    report_path = p.parent / "reports" / f"qa_report_{p.name}.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write("Corrupt:\n")
        f.write("\n".join(corrupt) + "\n")
        f.write("Duplicates:\n")
        f.write("\n".join([f"{a} == {b}" for a, b in duplicates]))

if __name__ == "__main__":
    dataset_qa_check("ml/datasets")
