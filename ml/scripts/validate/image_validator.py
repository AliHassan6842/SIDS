from pathlib import Path
from typing import Any

from PIL import Image, ImageFile, UnidentifiedImageError

# Allow loading truncated images if necessary, but here we might want to be strict
ImageFile.LOAD_TRUNCATED_IMAGES = False

# Maximum allowed pixels to prevent decompression bomb attacks
# e.g., 8192 * 8192 = 67_108_864
MAX_IMAGE_PIXELS = 100_000_000
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

class ImageValidator:
    """Validates images for dataset quality."""
    
    def __init__(
        self,
        min_width: int = 64,
        min_height: int = 64,
        max_width: int = 4096,
        max_height: int = 4096,
        max_file_size_bytes: int = 20 * 1024 * 1024  # 20MB
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        self.max_file_size_bytes = max_file_size_bytes

    def validate(self, file_path: str | Path) -> dict[str, Any]:
        """
        Validates a single image file.
        Returns a dictionary with 'valid' bool and 'issues' list.
        """
        path = Path(file_path)
        issues: list[dict[str, Any]] = []

        if not path.exists():
            return {"valid": False, "issues": [{"code": "FILE_NOT_FOUND", "severity": "ERROR"}], "requestedAction": "REMOVE"}
            
        if not path.is_file():
            return {"valid": False, "issues": [{"code": "NOT_A_FILE", "severity": "ERROR"}], "requestedAction": "REMOVE"}

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            issues.append({"code": "UNSUPPORTED_EXTENSION", "severity": "ERROR", "measurement": path.suffix.lower()})
            return {"valid": False, "issues": issues, "requestedAction": "REMOVE"}

        file_size = path.stat().st_size
        if file_size == 0:
            issues.append({"code": "EMPTY_FILE", "severity": "ERROR"})
            return {"valid": False, "issues": issues, "requestedAction": "REMOVE"}
            
        if file_size > self.max_file_size_bytes:
            issues.append({"code": "FILE_TOO_LARGE", "severity": "ERROR", "measurement": file_size, "threshold": self.max_file_size_bytes})

        try:
            with Image.open(path) as img:
                # Actual decode check
                img.verify()
        except UnidentifiedImageError:
            issues.append({"code": "DECODE_ERROR", "severity": "ERROR"})
            return {"valid": False, "issues": issues, "requestedAction": "REMOVE"}
        except Exception as e:
            issues.append({"code": "CORRUPT_IMAGE", "severity": "ERROR", "measurement": str(e)})
            return {"valid": False, "issues": issues, "requestedAction": "REMOVE"}
            
        # Image.verify() closes the file, need to reopen to get details
        try:
            with Image.open(path) as img:
                width, height = img.size
                num_pixels = width * height
                
                if width < self.min_width or height < self.min_height:
                    issues.append({"code": "RESOLUTION_TOO_LOW", "severity": "ERROR", "measurement": f"{width}x{height}"})
                if width > self.max_width or height > self.max_height:
                    issues.append({"code": "RESOLUTION_TOO_HIGH", "severity": "WARNING", "measurement": f"{width}x{height}"})
                    
                if num_pixels > MAX_IMAGE_PIXELS:
                    issues.append({"code": "PIXEL_COUNT_TOO_HIGH", "severity": "ERROR", "measurement": num_pixels})
                    
                mode = img.mode
                if mode not in ("RGB", "RGBA", "L"):
                    issues.append({"code": "UNSUPPORTED_COLOR_MODE", "severity": "WARNING", "measurement": mode})
                    
        except Exception as e:
             issues.append({"code": "READ_ERROR", "severity": "ERROR", "measurement": str(e)})

        valid = not any(issue.get("severity") == "ERROR" for issue in issues)
        action = "RETAKE" if not valid else "NONE"
        
        return {
            "valid": valid,
            "issues": issues,
            "requestedAction": action
        }

if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Validate an image.")
    parser.add_argument("image_path", type=str, help="Path to the image to validate")
    args = parser.parse_args()
    
    validator = ImageValidator()
    result = validator.validate(args.image_path)
    print(json.dumps(result, indent=2))
