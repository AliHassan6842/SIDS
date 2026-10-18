"""Repartition audited v1.1 BAU OOD components for class-disjoint open-set training."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections import Counter
from pathlib import Path


DATASET_VERSION = "sids-general-insect-classification-v1.2"
BASE_VERSION = "sids-general-insect-classification-v1.0"
AUDIT_VERSION = "sids-general-insect-classification-v1.1"
PARTITION_BY_SOURCE_LABEL = {
    "aphids": "train",
    "armyworm": "train",
    "bollworm": "calibration",
    "mites": "calibration",
    "sawfly": "test",
    "stem_borer": "test",
}


def link_or_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    base = workspace / "ml/data/prepared" / BASE_VERSION
    audited = workspace / "ml/data/prepared" / AUDIT_VERSION
    output = workspace / "ml/data/prepared" / DATASET_VERSION
    report_path = workspace / "ml/reports" / f"{DATASET_VERSION}-preparation.json"
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")

    for split in ("train", "val", "test"):
        for path in sorted((base / split).rglob("*")):
            relative = path.relative_to(base)
            if path.is_dir():
                (output / relative).mkdir(parents=True, exist_ok=True)
            else:
                link_or_copy(path, output / relative)

    audited_index = json.loads((audited / "source-index.json").read_text(encoding="utf-8"))
    base_index = json.loads((base / "source-index.json").read_text(encoding="utf-8"))
    index = list(base_index)
    counts: dict[str, Counter[str]] = {
        "train": Counter(),
        "calibration": Counter(),
        "test": Counter(),
    }
    for record in audited_index:
        label = record.get("source_coarse_label")
        if record.get("expected_outcome") != "UNKNOWN" or label not in PARTITION_BY_SOURCE_LABEL:
            continue
        partition = PARTITION_BY_SOURCE_LABEL[label]
        source_path = Path(record["source_path"])
        file_name = f"BAU_OPEN_{label}_{record['sha256'][:20]}{source_path.suffix.lower()}"
        destination = output / "unknown" / partition / label / file_name
        link_or_copy(source_path, destination)
        counts[partition][label] += 1
        index.append(
            {
                **record,
                "prepared_split": f"unknown/{partition}",
                "file_name": file_name,
                "unknown_training_role": partition,
            }
        )
    (output / "source-index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    report = {
        "schema_version": 1,
        "generated_at": "2026-08-26",
        "dataset_version": DATASET_VERSION,
        "status": "PREPARED_OPEN_SET_PRODUCT_CANDIDATE_NOT_PROMOTED",
        "base_known_dataset": BASE_VERSION,
        "ood_component_audit_dataset": AUDIT_VERSION,
        "known_splits_unchanged": True,
        "supported_coarse_labels": ["beetle", "grasshopper", "mosquito"],
        "internal_training_only_label": "unknown-insect",
        "unknown_partition_by_disjoint_source_class": {
            partition: sorted(label for label, value in PARTITION_BY_SOURCE_LABEL.items() if value == partition)
            for partition in ("train", "calibration", "test")
        },
        "unknown_counts": {partition: dict(sorted(values.items())) for partition, values in counts.items()},
        "preparation_source_report": "ml/reports/sids-general-insect-classification-v1.1-preparation.json",
        "preparation_source_report_sha256": sha256_file(
            workspace / "ml/reports/sids-general-insect-classification-v1.1-preparation.json"
        ),
        "leakage_evidence": "v1.1 global dHash<=2 component audit; no known/OOD near overlap",
        "limitations": [
            "Unknown training, calibration, and test source classes are disjoint.",
            "All labels remain coarse BAU folder labels.",
            "Agricultural imagery does not establish household-scene performance.",
            "Known test was previously observed by v1.0 research.",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
