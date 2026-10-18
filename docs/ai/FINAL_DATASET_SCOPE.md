# Final Dataset Scope

## Frozen product claim

The trained detection scope is **Rice only** and contains exactly two source-native IP102 labels:

| Model index | Product pest ID | IP102 category | Train / validation / test positive images | Train / validation / test boxes |
|---:|---|---:|---:|---:|
| 0 | `rice-leaf-roller` | 1, “rice leaf roller” | 99 / 25 / 35 | 109 / 26 / 39 |
| 1 | `rice-water-weevil` | 11, “rice water weevil” | 94 / 23 / 30 | 94 / 23 / 30 |

These are label strings, not independently verified biological species. No scientific-name mapping is asserted. The model must not be presented as a generic insect detector, a disease detector, a whole-field incidence estimator, or evidence for Cotton, Wheat, Maize, Tomato, or any other crop.

## Fetched sources and license constraints

The download ledger is `ml/data/fetched/FETCH_MANIFEST.json`; the source-specific tracked records are `ml/dataset-registry/sources/ip102-coco-v1.json` and `ml/dataset-registry/sources/bau-insectv2-v2.json`.

| Source | Local fetched archive | Size | SHA-256 | Terms and permitted role |
|---|---|---:|---|---|
| IP102 v1.1 COCO derivative | `ml/data/fetched/ip102/ip102-coco-v1.zip` | 798,292,200 bytes | `662187aae875b32d3b43db6c5a4f0cf6a2305ef83d95eddcff1df2c35ce26308` | Original publisher states academic use; contact the author for other purposes. Positive training/evaluation evidence for this academic FYP only. |
| BAU-Insectv2 v2 | `ml/data/fetched/bau-insectv2/BAU-Insectv2-v2.zip` | 64,389,120 bytes | `af2c13d87efd069af0cfc0a064f896b2b941cd8a01ffbd1588d6fb9b5b3881c7` | CC BY 4.0. Coarse unsupported-insect hard negatives and rejection probes only. |

IP102 contains 15,171 train images with 17,833 boxes and 3,798 test images with 4,444 boxes across 102 categories. All referenced images decoded successfully. The train annotations contain three image-dimension mismatches, one non-positive-area box, and three out-of-bounds boxes; selected records were filtered and converted by the tracked preparation script. The test annotations showed no audited bbox issue.

BAU contains 2,232 train and 384 test images across nine coarse folders and has no bounding boxes. Its published split is not safe for direct evaluation: 303 exact cross-split duplicate clusters cover 1,690 files. The audit found 473 perceptual components across all 2,616 valid images. BAU folder names are never equated to the two supported IP102 labels.

## Leakage-safe preparation

`sids-rice-pest-detection-v1.1` initially prepared three rice labels. Preparation removed 25 official-train images whose dHash distance was at most 2 from official test images, grouped train/validation by perceptual component, and removed four cross-class ambiguous images. Independent verification found no SHA-256 or dHash-distance-at-most-2 component crossing train/validation/test.

The initial three-class CPU test exposed weak `asiatic-rice-borer` evidence (test AP50 0.411 and AP50-95 0.175), so that label was excluded rather than promoted. `sids-rice-pest-detection-v1.2` retained the two defensible labels with 193/48/65 positive images and 203/49/69 boxes.

`sids-rice-pest-detection-v1.3` adds exactly 90 BAU original-train images—10 from each coarse folder—as empty-label YOLO hard negatives. Every selected hard negative is dHash-distance greater than 2 from every frozen BAU calibration/holdout component and from every other selected negative. COCO8 remains external probe-only material and contributes zero training images. Final image counts are 283 train, 48 validation, and 65 test; validation and test are byte-identical to v1.2.

Tracked reproducibility assets:

- `ml/scripts/datasets/prepare_sids_rice_pests.py`
- `ml/scripts/datasets/narrow_rice_scope_v1_2.py`
- `ml/scripts/datasets/prepare_sids_rice_pests_v1_3.py`
- `ml/dataset-registry/versions/sids-rice-pest-detection-v1.3.json`
- `ml/reports/sids-rice-pest-detection-v1.1-audit.json`
- `ml/reports/sids-rice-pest-detection-v1.3-preparation.json`

## Data separation

Downloaded archives and extraction trees live only under `ml/data/fetched/`. Deterministic converted YOLO trees live only under `ml/data/prepared/`. Training runs and checkpoints live only under `ml/runs/`. These directories are ignored by Git. Small provenance, split, preparation, configuration, evaluation, and model manifests are tracked separately. The promoted local runtime artifact is under `models/artifacts/`; its exact checksum is enforced by the runtime manifest. Raw/fetched data must never be mixed into prepared outputs or committed as if it were source code.

## Acceptance boundary

The promoted threshold is 0.66. On the frozen raw-model test, accepted predictions were 20/65 with 1.0 accepted precision; the remaining 45 were unknown. BAU holdout false accepts were 2/45 and COCO8 holdout false accepts were 0/4. After portrait-orientation normalization, the runtime path identifies 20/65 known fixtures while dimension validation rejects 22 as `SUBJECT_TOO_SMALL`; BAU and COCO8 false accepts remain 2/45 and 0/4. This is a deliberately high-precision, low-coverage FYP baseline—not production agricultural validation.
