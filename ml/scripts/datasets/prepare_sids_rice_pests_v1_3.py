"""Add leakage-safe BAU training-side hard negatives to the v1.2 detector.

BAU folder labels remain coarse and are never mapped to a supported pest. Selected
images receive empty YOLO label files and therefore teach background rejection only.
All perceptual components used by the frozen v1.2 calibration/holdout probes are
excluded before selection.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dhash(path: Path) -> int:
    with Image.open(path) as image:
        gray = image.convert("L").resize((9, 8))
        getter = getattr(gray, "get_flattened_data", gray.getdata)
        pixels = list(getter())
    return sum(
        (1 << (row * 8 + col))
        for row in range(8)
        for col in range(8)
        if pixels[row * 9 + col] > pixels[row * 9 + col + 1]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bau-train", type=Path, required=True)
    parser.add_argument("--frozen-probe-report", type=Path, required=True)
    parser.add_argument("--registry-output", type=Path, required=True)
    parser.add_argument("--report-output", type=Path, required=True)
    parser.add_argument("--per-class", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260822)
    args = parser.parse_args()

    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite prepared dataset: {args.output}")
    probe_report = json.loads(args.frozen_probe_report.read_text(encoding="utf-8"))
    probe_paths = [
        Path(path)
        for key in ("bau_calibration", "bau_holdout")
        for path in probe_report["fixtures"][key]
    ]
    probe_hashes = [dhash(path) for path in probe_paths]

    candidates: dict[str, list[tuple[str, int, Path]]] = defaultdict(list)
    invalid = 0
    excluded_probe_near_duplicates = 0
    for path in sorted(args.bau_train.rglob("*")):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        try:
            with Image.open(path) as image:
                image.verify()
            perceptual_hash = dhash(path)
        except Exception:
            invalid += 1
            continue
        if any((perceptual_hash ^ probe_hash).bit_count() <= 2 for probe_hash in probe_hashes):
            excluded_probe_near_duplicates += 1
            continue
        class_name = path.parent.name
        rank = hashlib.sha256(f"{args.seed}:{path.as_posix()}".encode()).hexdigest()
        candidates[class_name].append((rank, perceptual_hash, path))

    selected: list[tuple[str, int, Path]] = []
    selected_hashes: list[int] = []
    counts: dict[str, int] = {}
    rejected_selected_near_duplicates = 0
    for class_name in sorted(candidates):
        class_selected = 0
        for _, perceptual_hash, path in sorted(candidates[class_name]):
            if any((perceptual_hash ^ used).bit_count() <= 2 for used in selected_hashes):
                rejected_selected_near_duplicates += 1
                continue
            selected.append((class_name, perceptual_hash, path))
            selected_hashes.append(perceptual_hash)
            class_selected += 1
            if class_selected == args.per_class:
                break
        counts[class_name] = class_selected

    shutil.copytree(args.base, args.output)
    source_index_path = args.output / "source-index.json"
    source_index = json.loads(source_index_path.read_text(encoding="utf-8"))
    added_records = []
    for class_name, perceptual_hash, source_path in selected:
        digest = sha256(source_path)
        suffix = source_path.suffix.lower() or ".jpg"
        file_name = f"BAU_NEG_{class_name}_{digest[:16]}{suffix}"
        destination = args.output / "images" / "train" / file_name
        shutil.copy2(source_path, destination)
        (args.output / "labels" / "train" / f"{Path(file_name).stem}.txt").write_text(
            "", encoding="utf-8"
        )
        record = {
            "prepared_split": "train",
            "source_split": "train",
            "source_dataset": "bau-insectv2-v2",
            "source_path": str(source_path),
            "file_name": file_name,
            "source_coarse_label": class_name,
            "class_slug": None,
            "sha256": digest,
            "dhash": f"{perceptual_hash:016x}",
            "boxes": 0,
            "model_index": None,
            "training_role": "unsupported-insect-hard-negative",
        }
        source_index.append(record)
        added_records.append(record)
    source_index_path.write_text(json.dumps(source_index, indent=2) + "\n", encoding="utf-8")

    data_yaml = args.output / "data.yaml"
    data_yaml.write_text(
        "\n".join(
            [
                f"path: {args.output.resolve().as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                "  0: rice-leaf-roller",
                "  1: rice-water-weevil",
                "",
            ]
        ),
        encoding="utf-8",
    )

    report = {
        "schema_version": 1,
        "dataset_version": "sids-rice-pest-detection-v1.3",
        "derived_from": "sids-rice-pest-detection-v1.2",
        "hard_negative_source": "bau-insectv2-v2 original train folders only",
        "hard_negative_semantics": "empty YOLO labels; unsupported/background only",
        "selection_seed": args.seed,
        "requested_per_coarse_class": args.per_class,
        "selected_per_coarse_class": counts,
        "selected_total": len(selected),
        "invalid_candidates": invalid,
        "excluded_near_frozen_probe_component": excluded_probe_near_duplicates,
        "excluded_near_already_selected": rejected_selected_near_duplicates,
        "frozen_probe_report": str(args.frozen_probe_report),
        "frozen_bau_probe_images": len(probe_paths),
        "coco8_training_images": 0,
        "positive_split_counts_inherited": {
            "train": 193,
            "val": 48,
            "test": 65,
        },
        "final_split_counts": {
            "train": 193 + len(selected),
            "val": 48,
            "test": 65,
        },
        "selected_records": added_records,
    }
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    registry = {
        "schema_version": 1,
        "dataset_id": "sids-rice-pest-detection-v1.3",
        "task": "pest-detection",
        "status": "PREPARED_NOT_PROMOTED",
        "derived_from": "sids-rice-pest-detection-v1.2",
        "crop_scope": ["rice"],
        "supported_classes": ["rice-leaf-roller", "rice-water-weevil"],
        "scientific_name_mapping": None,
        "prepared_relative_path": str(args.output).replace("\\", "/"),
        "split_seed": args.seed,
        "positive_counts": {
            "train": 193,
            "val": 48,
            "test": 65,
        },
        "hard_negative_counts": {"train": len(selected), "val": 0, "test": 0},
        "final_image_counts": report["final_split_counts"],
        "leakage_evidence": (
            "All BAU dHash-distance<=2 components present in the frozen calibration/holdout "
            "probe list were excluded; selected hard negatives are mutually dHash-distance>2"
        ),
        "license": {
            "ip102": "Academic use only; contact original author for other purposes",
            "bau": "CC BY 4.0",
            "redistribution": "Raw and prepared images are not committed",
        },
    }
    args.registry_output.parent.mkdir(parents=True, exist_ok=True)
    args.registry_output.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected_total": len(selected), "counts": counts}))


if __name__ == "__main__":
    main()
