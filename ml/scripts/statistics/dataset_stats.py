import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


class DatasetStatistics:
    """Generates statistics for a dataset split or manifest."""
    
    def __init__(self, manifest_data: list[dict[str, Any]]):
        self.data = manifest_data
        
    def calculate_stats(self) -> dict[str, Any]:
        total_images = len(self.data)
        
        class_counter = Counter()
        source_counter = Counter()
        resolution_counter = Counter()
        
        total_annotations = 0
        corrupt_images = 0
        
        for item in self.data:
            # Source distribution
            source = item.get("source", "unknown")
            source_counter[source] += 1
            
            # Resolution
            width = item.get("width")
            height = item.get("height")
            if width and height:
                resolution_counter[f"{width}x{height}"] += 1
                
            # Corruption flag
            if item.get("is_corrupt", False) or item.get("valid") is False:
                corrupt_images += 1
                
            # Annotations
            annotations = item.get("annotations", [])
            total_annotations += len(annotations)
            
            for ann in annotations:
                class_id = ann.get("class_id", "unknown")
                class_counter[str(class_id)] += 1
                
        # Class imbalance calculation (max class count / min class count)
        class_counts = list(class_counter.values())
        if len(class_counts) > 0:
            max_class = max(class_counts)
            min_class = min(class_counts)
            imbalance_ratio = max_class / min_class if min_class > 0 else float('inf')
        else:
            imbalance_ratio = 0.0
            
        return {
            "total_images": total_images,
            "corrupt_images": corrupt_images,
            "total_annotations": total_annotations,
            "class_counts": dict(class_counter),
            "source_distribution": dict(source_counter),
            "common_resolutions": dict(resolution_counter.most_common(5)),
            "class_imbalance_ratio": imbalance_ratio
        }
        
    def generate_markdown(self, stats: dict[str, Any]) -> str:
        md = [
            "# Dataset Statistics",
            "",
            f"- **Total Images**: {stats['total_images']}",
            f"- **Corrupt Images**: {stats['corrupt_images']}",
            f"- **Total Annotations**: {stats['total_annotations']}",
            f"- **Class Imbalance Ratio**: {stats['class_imbalance_ratio']:.2f}",
            "",
            "## Class Counts",
            "| Class ID | Count |",
            "|----------|-------|"
        ]
        
        for cls_id, count in sorted(stats['class_counts'].items(), key=lambda x: x[1], reverse=True):
            md.append(f"| {cls_id} | {count} |")
            
        md.extend([
            "",
            "## Source Distribution",
            "| Source | Count |",
            "|--------|-------|"
        ])
        
        for src, count in sorted(stats['source_distribution'].items(), key=lambda x: x[1], reverse=True):
            md.append(f"| {src} | {count} |")
            
        return "\\n".join(md)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate dataset statistics.")
    parser.add_argument("manifest", type=str, help="Path to dataset JSON manifest")
    parser.add_argument("--format", choices=["json", "md", "both"], default="both", help="Output format")
    parser.add_argument("--output-dir", type=str, default=".", help="Directory to save output files")
    
    args = parser.parse_args()
    
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Error: Manifest {manifest_path} not found.")
        exit(1)
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # If the manifest is already split (has "train", "val", "test" keys), we can process each or flatten
    if isinstance(data, dict) and any(k in data for k in ["train", "val", "test"]):
        # Flatten for global stats
        flat_data = []
        for split_key in ["train", "val", "test"]:
            if split_key in data:
                flat_data.extend(data[split_key])
        data = flat_data
        
    generator = DatasetStatistics(data)
    stats = generator.calculate_stats()
    
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if args.format in ["json", "both"]:
        out_json = out_dir / f"{manifest_path.stem}_stats.json"
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        print(f"JSON stats written to {out_json}")
        
    if args.format in ["md", "both"]:
        out_md = out_dir / f"{manifest_path.stem}_stats.md"
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(generator.generate_markdown(stats))
        print(f"Markdown stats written to {out_md}")
