"""Add leakage-audited, class-disjoint BAU OOD evidence to general-insect v1.0.

The known-class split is copied unchanged. Unsupported BAU labels are pooled across
the publisher's leaky split, grouped globally by dHash distance, and assigned by
whole source class: aphids/armyworm/bollworm calibrate rejection while
mites/sawfly/stem_borer remain evaluation-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, UnidentifiedImageError


DATASET_VERSION = "sids-general-insect-classification-v1.1"
BASE_VERSION = "sids-general-insect-classification-v1.0"
OOD_CALIBRATION_LABELS = ("aphids", "armyworm", "bollworm")
OOD_TEST_LABELS = ("mites", "sawfly", "stem_borer")
DHASH_DISTANCE = 2


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def difference_hash(path: Path) -> int:
    with Image.open(path) as image:
        gray = image.convert("L").resize((9, 8))
        getter = getattr(gray, "get_flattened_data", gray.getdata)
        pixels = list(getter())
    value = 0
    for row in range(8):
        for column in range(8):
            offset = row * 9 + column
            value = (value << 1) | int(pixels[offset] > pixels[offset + 1])
    return value


def link_or_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def component_representatives(records: list[dict]) -> tuple[list[dict], list[list[dict]]]:
    parents = list(range(len(records)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    for left in range(len(records)):
        for right in range(left + 1, len(records)):
            if (records[left]["dhash"] ^ records[right]["dhash"]).bit_count() <= DHASH_DISTANCE:
                union(left, right)
    components: dict[int, list[dict]] = defaultdict(list)
    for index, record in enumerate(records):
        components[find(index)].append(record)
    clean, ambiguous = [], []
    for component in components.values():
        labels = {record["source_label"] for record in component}
        if len(labels) != 1:
            ambiguous.append(component)
            continue
        clean.append(
            min(
                component,
                key=lambda record: hashlib.sha256(record["path"].as_posix().encode()).hexdigest(),
            )
        )
    return clean, ambiguous


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    base = workspace / "ml/data/prepared" / BASE_VERSION
    output = workspace / "ml/data/prepared" / DATASET_VERSION
    source = workspace / "ml/data/fetched/bau-insectv2/extracted/extracted_folder/pest"
    report_path = workspace / "ml/reports" / f"{DATASET_VERSION}-preparation.json"
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    if not base.is_dir():
        raise FileNotFoundError(base)

    for path in sorted(base.rglob("*")):
        relative = path.relative_to(base)
        if path.is_dir():
            (output / relative).mkdir(parents=True, exist_ok=True)
        elif path.name != "source-index.json":
            link_or_copy(path, output / relative)

    records, invalid = [], Counter()
    for published_split in ("train", "test"):
        for label in (*OOD_CALIBRATION_LABELS, *OOD_TEST_LABELS):
            for path in sorted((source / published_split / label).glob("*")):
                if not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                    continue
                try:
                    with Image.open(path) as image:
                        image.verify()
                    records.append(
                        {
                            "path": path,
                            "published_split": published_split,
                            "source_label": label,
                            "sha256": sha256_file(path),
                            "dhash": difference_hash(path),
                        }
                    )
                except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as error:
                    invalid[type(error).__name__] += 1

    representatives, ambiguous = component_representatives(records)
    base_index = json.loads((base / "source-index.json").read_text(encoding="utf-8"))
    base_hashes = {record["sha256"] for record in base_index}
    base_dhashes = [int(record["dhash"], 16) for record in base_index]
    leakage_removed = []
    clean_representatives = []
    for record in representatives:
        if record["sha256"] in base_hashes or any(
            (record["dhash"] ^ known_hash).bit_count() <= DHASH_DISTANCE for known_hash in base_dhashes
        ):
            leakage_removed.append(record)
        else:
            clean_representatives.append(record)

    index = list(base_index)
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for record in clean_representatives:
        split = "calibration" if record["source_label"] in OOD_CALIBRATION_LABELS else "test"
        file_name = f"BAU_OOD_{record['source_label']}_{record['sha256'][:20]}{record['path'].suffix.lower()}"
        destination = output / "ood" / split / record["source_label"] / file_name
        link_or_copy(record["path"], destination)
        counts[split][record["source_label"]] += 1
        index.append(
            {
                "prepared_split": f"ood/{split}",
                "file_name": file_name,
                "class_slug": None,
                "expected_outcome": "UNKNOWN",
                "source_dataset": "bau-insectv2-v2",
                "source_coarse_label": record["source_label"],
                "source_published_split": record["published_split"],
                "source_path": str(record["path"]),
                "sha256": record["sha256"],
                "dhash": f"{record['dhash']:016x}",
            }
        )
    (output / "source-index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

    report = {
        "schema_version": 1,
        "generated_at": "2026-08-26",
        "dataset_version": DATASET_VERSION,
        "status": "PREPARED_PRODUCT_CANDIDATE_NOT_PROMOTED",
        "base_known_dataset": BASE_VERSION,
        "known_splits_unchanged": True,
        "supported_coarse_labels": ["beetle", "grasshopper", "mosquito"],
        "ood_calibration_labels": list(OOD_CALIBRATION_LABELS),
        "ood_test_labels": list(OOD_TEST_LABELS),
        "ood_counts": {split: dict(sorted(values.items())) for split, values in counts.items()},
        "source_valid_images": len(records),
        "invalid_images": dict(sorted(invalid.items())),
        "global_ood_representatives": len(representatives),
        "cross_label_ambiguous_components_removed": len(ambiguous),
        "cross_label_ambiguous_images_removed": sum(len(component) for component in ambiguous),
        "known_ood_near_duplicates_removed": len(leakage_removed),
        "dhash_distance": DHASH_DISTANCE,
        "leakage_policy": "No OOD representative is within dHash distance 2 of a known-class representative",
        "limitations": [
            "Supported and unsupported labels are coarse BAU folders, not verified species.",
            "OOD calibration and test use disjoint unsupported source classes.",
            "BAU imagery is agricultural and does not establish household-scene performance.",
            "The known test was previously observed during the v1.0 research run and is not a pristine test.",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
