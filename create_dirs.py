import os

dirs = [
    "ml/datasets/registry", "ml/datasets/manifests", "ml/datasets/mappings", "ml/datasets/reports",
    "ml/scripts/download", "ml/scripts/validate", "ml/scripts/deduplicate", "ml/scripts/split", "ml/scripts/convert",
    "ml/training/detection", "ml/training/classification", "ml/training/segmentation",
    "ml/evaluation/detection", "ml/evaluation/classification", "ml/evaluation/segmentation", 
    "ml/evaluation/calibration", "ml/evaluation/robustness", "ml/evaluation/deployment",
    "ml/experiments/configs", "ml/experiments/results", "ml/exports",
    "ml/model-registry/manifests", "ml/model-registry/model-cards",
    "knowledge/source-registry", "knowledge/ingestion", "knowledge/evaluation",
    "packages/contracts/openapi", "packages/contracts/json-schema", "packages/contracts/examples", 
    "packages/contracts/events", "packages/contracts/errors",
    "docs/datasets", "docs/research", "docs/api", "docs/ai/reports"
]

for d in dirs:
    os.makedirs(os.path.join(r"d:\vs code\uniSIDS\FinalYearProject", d), exist_ok=True)
print("Directories created.")
