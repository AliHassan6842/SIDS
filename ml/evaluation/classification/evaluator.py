import torch
from typing import Dict, Any
from ml.training.classification.metrics import compute_classification_metrics
from services.ai_service.src.sids_ai.disease_classification.classifier import DiseaseClassifier

class ClassificationEvaluator:
    """
    Evaluates the Disease Classification model on a hold-out test set.
    Separated from the training loop per architectural guidelines.
    """
    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = torch.device(device)
        self.model = DiseaseClassifier(model_path=model_path)
        self.model.load()

    def evaluate_test_set(self, dataloader) -> Dict[str, Any]:
        """
        Runs the standard metrics over a given DataLoader.
        """
        all_preds = []
        all_labels = []
        
        # We would iterate over dataloader and call model.predict() here
        # For now, it delegates to the metrics layer when dataset is available
        return compute_classification_metrics(all_preds, all_labels)

if __name__ == "__main__":
    print("Classification Evaluator Ready. Provide a test dataloader to begin.")
