from dataclasses import dataclass

import cv2
import numpy as np

from sids_ai.core.config import Settings
from sids_ai.schemas import QualityBand, QualitySummary, ValidationReason


@dataclass(frozen=True)
class QualityAssessment:
    valid: bool
    reason: ValidationReason | None
    insect_candidate: bool
    summary: QualitySummary


def assess_quality(rgb: np.ndarray, settings: Settings) -> QualityAssessment:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    brightness = float(gray.mean())
    blur_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    edges = cv2.Canny(gray, 70, 160)
    edge_density = float(np.count_nonzero(edges) / edges.size)
    insect_candidate = settings.candidate_edge_density_min <= edge_density <= settings.candidate_edge_density_max

    brightness_band = QualityBand.OK
    blur_band = QualityBand.OK
    reason: ValidationReason | None = None
    if brightness < settings.dark_mean:
        brightness_band = QualityBand.LOW
        reason = ValidationReason.TOO_DARK
    elif brightness > settings.bright_mean:
        brightness_band = QualityBand.HIGH
        reason = ValidationReason.TOO_BRIGHT
    elif edge_density < settings.candidate_edge_density_min:
        reason = ValidationReason.SUBJECT_TOO_SMALL
    elif edge_density > settings.candidate_edge_density_max:
        reason = ValidationReason.NO_INSECT_CANDIDATE
    elif blur_variance < settings.blur_variance_min:
        blur_band = QualityBand.LOW
        reason = ValidationReason.TOO_BLURRY

    return QualityAssessment(
        valid=reason is None,
        reason=reason,
        insect_candidate=insect_candidate,
        summary=QualitySummary(
            brightness=brightness_band,
            blur=blur_band,
            subjectSize=(
                QualityBand.OK
                if insect_candidate
                else QualityBand.LOW
                if edge_density < settings.candidate_edge_density_min
                else QualityBand.UNKNOWN
            ),
        ),
    )
