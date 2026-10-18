from types import SimpleNamespace

import numpy as np

from sids_ai.insect.model import PestDetector


class CapturingModel:
    def __init__(self) -> None:
        self.sources: list[np.ndarray] = []

    def predict(self, *, source, **kwargs):
        del kwargs
        self.sources = source
        return [SimpleNamespace(boxes=[]) for _ in source]


class FixedBoxModel(CapturingModel):
    def predict(self, *, source, **kwargs):
        del kwargs
        self.sources = source
        box = SimpleNamespace(
            cls=SimpleNamespace(item=lambda: 0),
            conf=SimpleNamespace(item=lambda: 0.9),
            xyxy=[SimpleNamespace(tolist=lambda: [20.0, 10.0, 80.0, 40.0])],
        )
        return [SimpleNamespace(boxes=[box]), *[SimpleNamespace(boxes=[]) for _ in source[1:]]]


def test_detector_converts_decoder_rgb_to_ultralytics_bgr() -> None:
    runtime = PestDetector.__new__(PestDetector)
    runtime.manifest = SimpleNamespace(
        crop_classes={"rice": ["rice-leaf-roller"]},
        input_size=320,
        acceptance_threshold=0.66,
        classes={0: "rice-leaf-roller"},
        evaluation_summary={},
    )
    runtime._model = CapturingModel()
    rgb = np.array([[[10, 20, 30]]], dtype=np.uint8)

    assert runtime.identify(rgb, "rice") is None
    assert runtime._model.sources[0].tolist() == [[[30, 20, 10]]]
    assert runtime._model.sources[0].flags.c_contiguous


def test_detector_normalizes_portrait_orientation_and_maps_bbox_back() -> None:
    runtime = PestDetector.__new__(PestDetector)
    runtime.manifest = SimpleNamespace(
        crop_classes={"rice": ["rice-leaf-roller"]},
        input_size=320,
        acceptance_threshold=0.66,
        classes={0: "rice-leaf-roller"},
        evaluation_summary={"inference_views": "FULL_PLUS_CENTER_80_PERCENT"},
    )
    runtime._model = FixedBoxModel()
    rgb = np.zeros((100, 50, 3), dtype=np.uint8)
    rgb[0, 0] = [10, 20, 30]

    detection = runtime.identify(rgb, "rice")

    assert detection is not None
    assert runtime._model.sources[0].shape == (50, 100, 3)
    assert len(runtime._model.sources) == 2
    assert runtime._model.sources[0].flags.c_contiguous
    assert np.isclose(detection.prediction.bbox.x, 0.2)
    assert np.isclose(detection.prediction.bbox.y, 0.2)
    assert np.isclose(detection.prediction.bbox.width, 0.6)
    assert np.isclose(detection.prediction.bbox.height, 0.6)
