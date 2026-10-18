# SIDS AI Expansion v2 Scope

## Status boundary

The active product model is unchanged: only `rice` with `rice-leaf-roller` and `rice-water-weevil` is promoted. Everything in this document is a prepared or trained **candidate**, not permission for the UI, Java catalog, or Python runtime to claim support.

The candidate crop mapping follows the eight super-classes in the primary [IP102 CVPR 2019 paper](https://openaccess.thecvf.com/content_CVPR_2019/papers/Wu_IP102_A_Large-Scale_Benchmark_Dataset_for_Insect_Pest_Recognition_CVPR_2019_paper.pdf). The paper groups IP102 into Rice, Corn, Wheat, Beet, Alfalfa, Vitis, Citrus, and Mango. v2 selects five of those groups and only source categories with at least 100 official-train and 25 official-test detection images.

## Five-crop detection candidate

Dataset version: `sids-multicrop-pest-detection-v2.0`  
Status: `PREPARED_CANDIDATE_NOT_TRAINED_NOT_PROMOTED`

| Crop | Candidate pest slug | IP102 ID / source label | Prepared train / val / test images | Prepared train / val / test boxes |
|---|---|---|---:|---:|
| rice | `rice-leaf-roller` | 1 / rice leaf roller | 101 / 25 / 35 | 106 / 31 / 39 |
| rice | `rice-water-weevil` | 11 / rice water weevil | 94 / 23 / 30 | 94 / 23 / 30 |
| corn | `corn-borer` | 23 / corn borer | 256 / 64 / 85 | 266 / 65 / 90 |
| corn | `corn-army-worm` | 24 / army worm | 109 / 27 / 41 | 115 / 30 / 41 |
| corn | `corn-aphids` | 25 / aphids | 528 / 132 / 174 | 857 / 187 / 278 |
| wheat | `english-grain-aphid` | 28 / english grain aphid | 78 / 19 / 26 | 177 / 53 / 60 |
| wheat | `wheat-sawfly` | 35 / wheat sawfly | 83 / 21 / 28 | 89 / 22 / 29 |
| beet | `flea-beetle` | 38 / flea beetle | 217 / 54 / 69 | 245 / 58 / 74 |
| beet | `cabbage-army-worm` | 39 / cabbage army worm | 122 / 30 / 49 | 135 / 30 / 56 |
| beet | `beet-army-worm` | 40 / beet army worm | 217 / 55 / 83 | 223 / 55 / 83 |
| citrus | `icerya-purchasi` | 77 / Icerya purchasi Maskell | 92 / 23 / 32 | 168 / 52 / 59 |
| citrus | `prodenia-litura` | 87 / Prodenia litura | 231 / 58 / 83 | 247 / 62 / 85 |

Total: 2,128 train images / 2,722 boxes; 531 validation images / 668 boxes; 735 untouched test images / 924 boxes.

Only images containing one unique COCO source category are used. This avoids treating an unselected annotated pest as background. Preparation removed 172 official-train images within dHash distance 2 of official test, then removed 109 images in perceptual components spanning different selected labels. The final independent validator decoded every prepared image, parsed every label, found no missing/orphan label, and found zero SHA or dHash-distance-at-most-2 overlap for train/validation, train/test, and validation/test.

No multi-crop training metric exists. A meaningful local run was not launched: the two-core i7-6600U needed 0.180 hours for only two 320 px epochs on 283 images, while v2 has 2,128 training images and 12 labels. The tracked GPU configuration uses 50 epochs at 640 px and requires independent test, per-crop macro, per-class, rejection, and runtime gates before any manifest promotion.

## General-insect research candidate

Source: locally fetched [BAU-Insectv2 v2](https://data.mendeley.com/datasets/x2c6c8thdk/2), CC BY 4.0.  
Dataset version: `sids-general-insect-classification-v1.0`  
Labels: `beetle`, `grasshopper`, `mosquito`.

These are BAU folder-level coarse labels. They are not species identifications and the dataset is agricultural imagery, not a household-scene benchmark. The mode must be described as general-insect research, not household insect identification.

The unsafe BAU published folders supplied 1,009 files for these labels. Global dHash-distance-at-most-2 grouping reduced them to 186 independent components. One representative per component was split as:

| Coarse label | Train | Validation | Test |
|---|---:|---:|---:|
| beetle | 42 | 9 | 9 |
| grasshopper | 42 | 9 | 9 |
| mosquito | 46 | 10 | 10 |

An executed eight-epoch frozen MobileNetV3-small CPU linear probe finished in 108.1 seconds. Best validation macro-F1 was 0.9280. The untouched 28-image test produced accuracy 0.9643 and macro-F1 0.9628: beetle 9/9, grasshopper 8/9, and mosquito 10/10. Test inference was 45.9 ms/image. The local ignored checkpoint is 6,203,625 bytes with SHA-256 `38e91e1923086ef1551535ac6dd7c417dc359b75b0f39663e12c060164bed86f`.

Despite those closed-set results, promotion is blocked. The test has only 9-10 independent examples per label, no household scenes, no random-object/unknown/OOD gate, and no approved production classifier contract. The checkpoint remains under `ml/runs/`, not `models/`.

## Opt-in active learning

The workflow under `ml/active_learning/` is manual and fail-closed:

1. Deterministically select unknown, confidence-band, or small-margin inference records.
2. Require a human decision, reviewer identity, review timestamp, unchanged SHA/dHash, crop-specific allowlisted labels, and normalized boxes.
3. Assign whole capture groups to train/validation/test.
4. Materialize only approved rows into a new dataset version. Exact or dHash-distance-at-most-2 matches to the base public data fail closed.
5. Retrain into `ml/runs/`; execute public, grouped-field, rejection, and runtime gates.
6. Promote only through a separate reviewed change. The workflow never writes `models/`.

The full select → seal → materialize smoke executed with one mechanics-only fixture. It selected one record, sealed one human-reviewed negative, added it to an isolated candidate workspace, and produced no model or promotion change.

## Reproducibility files

- `ml/scripts/datasets/prepare_multicrop_v2.py`
- `ml/scripts/datasets/prepare_general_insects_v1.py`
- `ml/evaluation/detection/validate_prepared_yolo.py`
- `ml/dataset-registry/versions/sids-multicrop-pest-detection-v2.0.json`
- `ml/dataset-registry/versions/sids-general-insect-classification-v1.0.json`
- `ml/reports/sids-multicrop-pest-detection-v2.0-preparation.json`
- `ml/reports/sids-multicrop-pest-detection-v2.0-validation.json`
- `ml/reports/sids-general-insect-classification-v1.0-preparation.json`
- `ml/reports/sids-general-insect-classification-v1.0-short-cpu.json`
- `ml/model-registry/pretrained/mobilenet-v3-small-imagenet1k-v1.json`
- `ml/training/detection/configs/sids-multicrop-pest-detection-v2.0.json`
- `ml/training/classification/train_general_insects.py`
- `ml/training/classification/configs/sids-general-insect-classification-v1.0.json`
- `ml/active_learning/README.md`
- `ml/active_learning/configs/sids-multicrop-v2.json`
- `ml/active_learning/review_schema.py`
- `ml/active_learning/select_review_candidates.py`
- `ml/active_learning/seal_review_batch.py`
- `ml/active_learning/materialize_retrain_candidate.py`
- `ml/active_learning/fixtures/inference-example.jsonl`
- `ml/active_learning/fixtures/reviewed-example.jsonl`
- `ml/reports/sids-multicrop-v2-active-learning-smoke.json`

Fetched archives/extractions remain under ignored `ml/data/fetched/`; deterministic prepared material and private review data remain under ignored `ml/data/prepared/`; runs/checkpoints remain under ignored `ml/runs/`. Only compact provenance, configuration, source-index rules, aggregate reports, and manifests are tracked.
