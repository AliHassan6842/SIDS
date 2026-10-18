# Final Model Report

## Outcome

`sids-rice-pest-detector` v1.0.0 remains the promoted primary bounded academic FYP baseline for two Rice pest labels. Compose uses `models/manifests/sids-pest-detector.json`, which checksum-verifies `models/artifacts/sids-rice-pest-detector-v1.0.0.pt` before loading.

A second checksum-verified detector, `sids-rice-pest-detector-small-subject` v1.1.0, is promoted only as a bounded fallback when the quality reason is `SUBJECT_TOO_SMALL`. It does not replace the primary detector and never runs for other rejected-image reasons.

Artifact SHA-256: `b3af4057f3d59c21efd27266ee519fe487c0433468f641973b3f89290ea674bc`  
Artifact size: 5,427,290 bytes  
Architecture/input: YOLO11n detection, 320 px  
Acceptance threshold: 0.66

Small-subject fallback SHA-256: `58e305fa035a41225463bd7dec53a272cc68ef91d2864a94e1084ae704d5063e`  
Fallback architecture/input: YOLO11n detection, 480 px, full plus centered 80-percent view  
Fallback acceptance threshold: 0.75

## Small-subject fallback evaluation

The v1.4 experiment fully fine-tuned the v1.3 checkpoint for six deterministic CPU epochs. Validation reached precision 0.943, recall 0.945, mAP50 0.981, and mAP50-95 0.514. The selected 480-pixel two-view runtime achieved 23/65 correct held-out known detections with accepted precision 0.9583, 1/45 BAU false accepts, and 0/4 COCO8 false accepts at threshold 0.75. A 640-pixel full-view alternative was rejected because its known correct-detection rate was only 0.2308, below the predeclared 0.30 gate.

Runtime loading of the fallback manifest identified 21/65 known fixtures, 0/45 BAU fixtures, and 0/4 COCO8 fixtures; malformed JPEG input was rejected. The supplied adult water-weevil image was not added to training. As an external probe, it was identified at confidence 0.8669 directly and 0.8621 through the live browser → Java → Python → PostgreSQL workflow.

## Training and formal evaluation

The final v1.3 run started from the v1.2 best checkpoint and trained for two CPU epochs on 193 positive images plus 90 leakage-safe BAU empty-label hard negatives. It completed in 0.180 hours on an Intel Core i7-6600U.

| Split / class | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| Validation overall, 48 images / 49 boxes | 0.575 | 0.776 | 0.799 | 0.394 |
| Test overall, 65 images / 69 boxes | 0.721 | 0.645 | 0.730 | 0.375 |
| Test rice-leaf-roller | 0.624 | 0.590 | 0.654 | 0.313 |
| Test rice-water-weevil | 0.819 | 0.700 | 0.807 | 0.438 |

Ultralytics reported 74.9 ms inference per test image at 320 px on CPU. After portrait-orientation normalization, the tracked runtime-component smoke measured 118.9 ms end-to-end per known fixture, including decode/sanitize and early dimension rejection.

## Threshold and rejection evidence

Threshold selection used only IP102 validation, 45 frozen BAU calibration probes, and four COCO8 calibration probes. The rule required accepted precision at least 0.80, BAU false-accept rate at most 0.05, and zero COCO8 calibration accepts. It selected 0.66.

| Executed category | Result | Status |
|---|---|---|
| Known IP102 held-out pests | 20/65 correctly localized and accepted; accepted precision 1.0 | PASS against the predeclared 0.30 correct-detection-rate minimum (actual 0.3077) |
| Unsupported BAU insects | 2/45 false accepts | PASS against 0.10 maximum (actual 0.0444) |
| COCO8 non-insect/random objects | 0/4 false accepts | PASS against 0.10 maximum |
| Malformed 93-byte JPEG | Runtime returns/reports `INVALID_IMAGE`; focused integration suite reports HTTP 400 before inference | PASS |

COCO8 is regression-probe support only, not product evidence or pest-training evidence. BAU is coarse unsupported-input evidence and is not mapped to a supported species.

## Runtime smoke

The exact default manifest and checksum-verified artifact were loaded through runtime components. Portrait captures are rotated clockwise for inference and their boxes are mapped back to the original image. Results were 20/65 known fixtures identified, 2/45 BAU fixtures identified, 0/4 COCO8 fixtures identified, and the malformed JPEG rejected. Dimension validation rejected 22/65 known and 36/45 BAU images as `SUBJECT_TOO_SMALL` before inference. The BAU/COCO false-accept counts did not increase after the orientation repair.

## Promotion decision and limitations

Promotion is appropriate only for the explicitly bounded FYP claim because every declared gate was executed and passed after the BAU-only hard-negative refinement. The v1.2 candidate remains recorded under `models/manifests/candidates/`; it was rejected after one of four COCO8 holdout images was falsely accepted. The v1.1.0 full replacement candidate was also rejected as a primary detector because it regressed one earlier portrait probe; only its higher-threshold small-subject path is promoted.

The v1.0.0 detector is not production-ready agricultural evidence. Its selected threshold leaves 45/65 known raw-model test images unknown, and end-to-end runtime coverage is 20/65 after orientation normalization and dimension filtering. IP102 terms restrict the present evidence to academic use. A stronger release requires a larger licensed, field-representative Rice dataset, repeated geographic/device holdouts, expanded non-insect and unsupported-insect fixtures, calibration confidence intervals, and the tracked GPU command in `ml/training/detection/configs/sids-rice-pest-detection-v1.3.json`.
