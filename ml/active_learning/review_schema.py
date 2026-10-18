"""Shared validation primitives for the opt-in reviewed-data workflow."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image


SAFE_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported active-learning config schema")
    return config


def validate_safe_token(value: str, field: str) -> str:
    if not SAFE_TOKEN.fullmatch(value):
        raise ValueError(f"{field} must be a safe 1-128 character token")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def difference_hash(path: Path) -> str:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        gray = image.convert("L").resize((9, 8))
        getter = getattr(gray, "get_flattened_data", gray.getdata)
        pixels = list(getter())
    value = 0
    for row in range(8):
        for column in range(8):
            offset = row * 9 + column
            value = (value << 1) | int(pixels[offset] > pixels[offset + 1])
    return f"{value:016x}"


def resolve_bounded_image(image_root: Path, relative_path: str) -> Path:
    root = image_root.resolve()
    candidate = (root / relative_path).resolve()
    if candidate == root or root not in candidate.parents:
        raise ValueError(f"Image path escapes the configured root: {relative_path}")
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    return candidate


def validate_bbox(bbox: dict[str, Any]) -> None:
    required = {"x", "y", "width", "height"}
    if set(bbox) != required:
        raise ValueError(f"bbox must contain exactly {sorted(required)}")
    x, y, width, height = (float(bbox[key]) for key in ("x", "y", "width", "height"))
    if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > 1 or y + height > 1:
        raise ValueError("bbox must be normalized, positive, and contained in the image")


def assigned_split(capture_group: str, seed: int, ratios: dict[str, float]) -> str:
    if abs(sum(float(value) for value in ratios.values()) - 1.0) > 1e-9:
        raise ValueError("Review split ratios must sum to one")
    value = int(hashlib.sha256(f"{seed}:{capture_group}".encode()).hexdigest()[:16], 16)
    position = value / float(0xFFFFFFFFFFFFFFFF)
    cumulative = 0.0
    for split in ("train", "val", "test"):
        cumulative += float(ratios[split])
        if position <= cumulative:
            return split
    return "test"
