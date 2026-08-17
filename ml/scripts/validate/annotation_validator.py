from pathlib import Path
from typing import Any


class AnnotationValidator:
    """Validates YOLO format bounding box annotations."""
    
    def __init__(self, max_classes: int = 100):
        self.max_classes = max_classes

    def validate_yolo_file(self, file_path: str | Path, image_exists: bool = True) -> dict[str, Any]:
        """
        Validates a YOLO annotation text file.
        Format per line: <class_id> <x_center> <y_center> <width> <height>
        """
        path = Path(file_path)
        issues: list[dict[str, Any]] = []

        if not path.exists():
            return {"valid": False, "issues": [{"code": "ANNOTATION_MISSING", "severity": "ERROR"}], "requestedAction": "REMOVE"}
            
        if not image_exists:
            issues.append({"code": "ORPHAN_ANNOTATION", "severity": "ERROR"})
            return {"valid": False, "issues": issues, "requestedAction": "REMOVE"}

        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            issues.append({"code": "FILE_READ_ERROR", "severity": "ERROR", "measurement": str(e)})
            return {"valid": False, "issues": issues, "requestedAction": "REMOVE"}

        if not lines:
            issues.append({"code": "EMPTY_LABEL_FILE", "severity": "WARNING"})
            return {"valid": True, "issues": issues, "requestedAction": "NONE"} # empty can mean background image

        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue
                
            parts = line.split()
            if len(parts) != 5:
                issues.append({"code": "MALFORMED_YOLO_LINE", "severity": "ERROR", "measurement": f"line {line_num}: {len(parts)} parts"})
                continue
                
            try:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                if class_id < 0 or class_id >= self.max_classes:
                    issues.append({"code": "INVALID_CLASS_ID", "severity": "ERROR", "measurement": f"line {line_num}: {class_id}"})
                    
                for val, name in [(x_center, "x_center"), (y_center, "y_center"), (width, "width"), (height, "height")]:
                    if val < 0.0 or val > 1.0:
                        issues.append({"code": "BBOX_OUT_OF_BOUNDS", "severity": "ERROR", "measurement": f"line {line_num} {name}: {val}"})
                        
                if width <= 0 or height <= 0:
                    issues.append({"code": "BBOX_ZERO_AREA", "severity": "ERROR", "measurement": f"line {line_num} w:{width} h:{height}"})
                    
                if x_center - (width / 2) < 0.0 or x_center + (width / 2) > 1.0 or y_center - (height / 2) < 0.0 or y_center + (height / 2) > 1.0:
                    issues.append({"code": "BBOX_EXCEEDS_IMAGE", "severity": "WARNING", "measurement": f"line {line_num}"})
                    
            except ValueError:
                issues.append({"code": "NON_NUMERIC_BBOX_DATA", "severity": "ERROR", "measurement": f"line {line_num}"})

        valid = not any(issue.get("severity") == "ERROR" for issue in issues)
        action = "FIX_ANNOTATION" if not valid else "NONE"
        
        return {
            "valid": valid,
            "issues": issues,
            "requestedAction": action
        }

if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Validate a YOLO annotation file.")
    parser.add_argument("annotation_path", type=str, help="Path to the txt file")
    parser.add_argument("--no-image", action="store_true", help="Set if the corresponding image is missing")
    args = parser.parse_args()
    
    validator = AnnotationValidator()
    result = validator.validate_yolo_file(args.annotation_path, image_exists=not args.no_image)
    print(json.dumps(result, indent=2))
