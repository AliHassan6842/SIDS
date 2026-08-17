
from sids_ai.schemas.analysis import QualityIssue


def evaluate_resolution(width: int, height: int, min_width: int, min_height: int) -> list[QualityIssue]:
    issues = []
    if width < min_width or height < min_height:
        # Find the limiting dimension for reporting
        measurement = float(min(width, height))
        threshold = float(min(min_width, min_height))
        
        issues.append(QualityIssue(
            code="RESOLUTION_TOO_LOW",
            severity="ERROR",
            measurement=measurement,
            threshold=threshold
        ))
    return issues
