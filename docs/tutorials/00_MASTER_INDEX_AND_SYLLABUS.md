# SIDS Machine Learning & Computer Vision Master Syllabus
**Curriculum Structure:** 5 Comprehensive Modules with Executable Companion Scripts  
**Domain:** Agricultural Pest Vision, Knowledge Distillation, Low-RAM Edge Optimization  
**Location:** [`docs/tutorials/`](file:///d:/vs%20code/uniSIDS/FinalYearProject/docs/tutorials/) & [`ml/tutorials/`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/)

---

## 🎓 The 5 Specialized Tutor Subagents

To fulfill your request for personalized and deep tutoring, 5 specialized AI tutors have been registered in the system:

1. **`tutor_vision_math`:** Expert in image decoding, numerical matrices, 3D tensor transformation ($C \times H \times W$), normalization mathematics, and spatial coordinates (Pascal VOC $\leftrightarrow$ COCO $\leftrightarrow$ YOLO).
2. **`tutor_dataset_pipeline`:** Expert in dataset structuring, COCO JSON schemas, custom PyTorch `Dataset` and `DataLoader` architecture, variable-length collation, and Teacher-VLM Zero-Shot auto-labeling.
3. **`tutor_architectures`:** Expert in multi-task deep networks, Classification Heads (CrossEntropy), Bounding Box Regression Heads (CIoU / Smooth L1), YOLO internals, and Vision Transformer (ViT) self-attention.
4. **`tutor_distillation`:** Expert in Teacher-Student Knowledge Distillation, Temperature Scaling ($\tau$), "Dark Knowledge" extraction, KL-Divergence loss formulation, and crafting deployable `.pt` weight files.
5. **`tutor_optimization_edge`:** Expert in detection evaluation metrics (IoU, Precision, Recall, mAP@0.5:0.95), Open-Set OOD confidence calibration, INT8 post-training quantization, and $<45\text{MB}$ mobile RAM profiling.

---

## 📚 Master Curriculum & Companion Code Map

| Module # | Textbook (Comprehensive Markdown) | Executable Script (Run & Test Live) | Core Concepts Taught |
| :--- | :--- | :--- | :--- |
| **01** | [`01_COMPUTER_VISION_MATH_AND_TENSORS.md`](file:///d:/vs%20code/uniSIDS/FinalYearProject/docs/tutorials/01_COMPUTER_VISION_MATH_AND_TENSORS.md) | [`01_image_to_numerical_tensor.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/01_image_to_numerical_tensor.py) | Pixel matrices, HWC vs CHW, ImageNet standardization, VOC/COCO/YOLO math, Instance Mask Hadamard isolation. |
| **02** | [`02_DATASET_PARSING_AND_VLM_PIPELINES.md`](file:///d:/vs%20code/uniSIDS/FinalYearProject/docs/tutorials/02_DATASET_PARSING_AND_VLM_PIPELINES.md) | [`02_dataset_json_and_dataloader.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/02_dataset_json_and_dataloader.py) | COCO JSON schema, variable bounding boxes problem, custom PyTorch `collate_fn`, Qwen2.5-VL Zero-Shot pseudo-labeler. |
| **03** | [`03_NEURAL_ARCHITECTURES_YOLO_SEG_TRANSFORMERS.md`](file:///d:/vs%20code/uniSIDS/FinalYearProject/docs/tutorials/03_NEURAL_ARCHITECTURES_YOLO_SEG_TRANSFORMERS.md) | [`03_classification_regression_and_yolo.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/03_classification_regression_and_yolo.py) | Softmax CrossEntropy, CIoU regression, Multi-Task loss weighting, YOLO PANet backbone, ViT patch self-attention. |
| **04** | [`04_KNOWLEDGE_DISTILLATION_AND_WEIGHT_CRAFTING.md`](file:///d:/vs%20code/uniSIDS/FinalYearProject/docs/tutorials/04_KNOWLEDGE_DISTILLATION_AND_WEIGHT_CRAFTING.md) | [`04_knowledge_distillation_pipeline.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/04_knowledge_distillation_pipeline.py) | Teacher-Student transfer, Hinton loss, temperature scaling ($\tau$), dark knowledge, saving `.pt` weights with SHA-256. |
| **05** | [`05_BENCHMARKING_QUANTIZATION_AND_EDGE_DEPLOYMENT.md`](file:///d:/vs%20code/uniSIDS/FinalYearProject/docs/tutorials/05_BENCHMARKING_QUANTIZATION_AND_EDGE_DEPLOYMENT.md) | [`05_benchmark_calibration_and_quantization.py`](file:///d:/vs%20code/uniSIDS/FinalYearProject/ml/tutorials/05_benchmark_calibration_and_quantization.py) | IoU matching, Precision/Recall/mAP, Open-Set OOD rejection, INT8 dynamic quantization, mobile latency profiling. |

---

## 🚀 How to Execute the Entire Tutorial Suite in Terminal

You can run each script step-by-step from your project root:

```powershell
# Activate your AI service virtual environment:
services\ai-service\.venv\Scripts\Activate.ps1

# Run Module 1: Image Tensors & Coordinate Math
python ml/tutorials/01_image_to_numerical_tensor.py

# Run Module 2: COCO JSON & PyTorch DataLoaders
python ml/tutorials/02_dataset_json_and_dataloader.py

# Run Module 3: Neural Networks & Multi-Task Loss
python ml/tutorials/03_classification_regression_and_yolo.py

# Run Module 4: Knowledge Distillation & Weight Generation
python ml/tutorials/04_knowledge_distillation_pipeline.py

# Run Module 5: Metrics, OOD Calibration & INT8 Quantization
python ml/tutorials/05_benchmark_calibration_and_quantization.py
```

All 5 scripts are completely self-contained, generate their own synthetic data and annotations, compute real mathematical operations, and produce verified zero-error outputs!
