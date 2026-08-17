# Model Benchmark Report

## 1. Overview
This report documents the performance and deployment footprint comparison of various models targeted for the Smart Insect Detection System (SIDS). The metrics focus on accuracy, latency, artifact size, and resource consumption to determine feasibility for production environments and potential edge/mobile devices.

## 2. Models Evaluated
- **Model A**: (e.g., YOLO11n - Pest Detection)
- **Model B**: (e.g., RF-DETR Nano - Pest Detection)
- **Model C**: (e.g., MobileNetV4 - Disease Classification)

## 3. Hardware & Environment Context
- **CPU**: (e.g., AMD EPYC / Intel Xeon, cores allocated)
- **GPU**: (e.g., None, or NVIDIA T4 / A10G)
- **RAM**: (e.g., 16 GB)
- **OS**: (e.g., Ubuntu 22.04 / Windows 11)
- **Framework Versions**: (e.g., PyTorch 2.3.0, ONNXRuntime 1.18.0)
- **Benchmark Batch Size**: (e.g., 1)

## 4. Deployment Metrics (Latency & Size)

| Model | Task | Artifact Size (MB) | Cold Load Time (ms) | Warm Latency (ms) | p50 Latency (ms) | p95 Latency (ms) | Peak RAM (MB) |
|-------|------|--------------------|---------------------|-------------------|------------------|------------------|---------------|
| *Example Model* | *Example* | *6.5* | *150.0* | *12.3* | *12.1* | *14.5* | *45.2* |
| Model A | Detection | - | - | - | - | - | - |
| Model B | Detection | - | - | - | - | - | - |
| Model C | Classification | - | - | - | - | - | - |

*(Note: Use `ml/evaluation/deployment/benchmark.py` to populate these metrics for real models)*

## 5. Accuracy Metrics (Effectiveness)

| Model | Task | Dataset Version | mAP50 / Accuracy | mAP50-95 / Macro F1 | Recall | Small-Object AP (Optional) |
|-------|------|-----------------|------------------|---------------------|--------|----------------------------|
| Model A | Detection | v1.0 | 0.85 | 0.55 | 0.82 | 0.40 |
| Model C | Classification | v1.0 | 0.92 | 0.88 | 0.91 | N/A |

## 6. Uncertainty & Failure Modes
- **Model A (Detection)**: (e.g., "Struggles with heavy occlusion. High confidence on misclassified background objects.")
- **Model C (Classification)**: (e.g., "Poor calibration on out-of-distribution blur images; frequently overconfident.")

## 7. Licensing & Feasibility
- **Model A**: (e.g., AGPL-3.0 - Review required for commercial service deployment vs client-side use)
- **Model C**: (e.g., Apache-2.0 - Fully permissive)
- **Mobile Feasibility**: (e.g., Model A memory footprint too large for edge device X, suitable for cloud execution)

## 8. Conclusions & Selected Model
- **Selected Detection Model**: [Name]
- **Selected Classification Model**: [Name]
- **Justification**: (e.g., "Chosen due to the optimal balance between p95 latency (<50ms) and strong Macro F1 score on the validation set. Memory requirements fit comfortably within the 512MB limit allocated for AI microservices.")
