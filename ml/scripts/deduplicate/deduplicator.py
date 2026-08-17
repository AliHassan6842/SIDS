import hashlib
from pathlib import Path
from typing import Any

try:
    import imagehash
    from PIL import Image
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False


class Deduplicator:
    """Finds exact and near duplicates in an image dataset."""
    
    def __init__(self, hash_size: int = 8, hash_threshold: int = 5):
        self.hash_size = hash_size
        self.hash_threshold = hash_threshold
        
    def _compute_sha256(self, path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
        
    def _compute_phash(self, path: Path) -> Any:
        if not IMAGEHASH_AVAILABLE:
            raise RuntimeError("imagehash and Pillow are required for pHash computation.")
        with Image.open(path) as img:
            return imagehash.phash(img, hash_size=self.hash_size)
            
    def find_duplicates(self, image_paths: list[str | Path]) -> dict[str, Any]:
        """
        Scans a list of images and groups them by exact matches (SHA-256)
        and near-duplicate matches (pHash).
        """
        exact_hashes: dict[str, list[str]] = {}
        perceptual_hashes: list[tuple[str, Any]] = []
        
        # 1. Compute hashes
        for path_str in image_paths:
            path = Path(path_str)
            if not path.exists() or not path.is_file():
                continue
                
            try:
                # Exact Hash
                sha_hash = self._compute_sha256(path)
                if sha_hash not in exact_hashes:
                    exact_hashes[sha_hash] = []
                exact_hashes[sha_hash].append(str(path))
                
                # Perceptual Hash
                if IMAGEHASH_AVAILABLE:
                    p_hash = self._compute_phash(path)
                    perceptual_hashes.append((str(path), p_hash))
            except Exception as e:
                print(f"Error processing {path}: {e}")
                
        # 2. Group Exact Duplicates
        exact_duplicates = [paths for paths in exact_hashes.values() if len(paths) > 1]
        
        # 3. Group Near Duplicates (connected components)
        # O(N^2) naive approach, appropriate for moderate sized datasets or batch processing
        near_duplicate_clusters: list[set[str]] = []
        if IMAGEHASH_AVAILABLE:
            visited: set[str] = set()
            
            for i, (path1, hash1) in enumerate(perceptual_hashes):
                if path1 in visited:
                    continue
                    
                current_cluster = {path1}
                visited.add(path1)
                
                for j, (path2, hash2) in enumerate(perceptual_hashes[i+1:], start=i+1):
                    if path2 in visited:
                        continue
                        
                    if hash1 - hash2 <= self.hash_threshold:
                        current_cluster.add(path2)
                        visited.add(path2)
                        
                if len(current_cluster) > 1:
                    near_duplicate_clusters.append(current_cluster)
                    
        return {
            "exact_duplicate_clusters": exact_duplicates,
            "near_duplicate_clusters": [list(cluster) for cluster in near_duplicate_clusters]
        }

if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Find image duplicates in a directory.")
    parser.add_argument("directory", type=str, help="Directory containing images to deduplicate")
    parser.add_argument("--threshold", type=int, default=5, help="Hamming distance threshold for pHash")
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist.")
        exit(1)
        
    image_paths = list(directory.glob("*.jpg")) + list(directory.glob("*.png")) + list(directory.glob("*.jpeg"))
    
    deduplicator = Deduplicator(hash_threshold=args.threshold)
    results = deduplicator.find_duplicates(image_paths)
    
    print(json.dumps(results, indent=2))
