# AI service boundary

This directory is reserved for the future production Python/FastAPI inference runtime owned by the AI / Research Lead. No service or Python package is initialized in F0.

Planned technology includes FastAPI, Pydantic, PyTorch, OpenCV, Pillow, ONNX Runtime, NumPy, Albumentations, pytest, Ruff, and Pyright or Mypy.

The runtime will validate image quality, route supported problem types, execute approved pest/disease/severity models, compute embeddings and similar-case features, express uncertainty and unknown/OOD outcomes, and return inference/model metadata.

Python performs computation. It must not choose pesticides, dosages, legal treatments, economic thresholds, farm-wide risk, user authorization, or farm permissions.
