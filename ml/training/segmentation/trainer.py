import logging

logger = logging.getLogger(__name__)

class SegmentationTrainer:
    """
    Stub for Segmentation Training Framework.
    
    FULL DATASET-DEPENDENT TRAINING IS EXPLICITLY BLOCKED.
    Reason: Adequate segmentation dataset is currently unavailable. 
    Do NOT fabricate masks from classification datasets.
    """
    
    def __init__(self, config_path: str = ""):
        self.config_path = config_path
        logger.warning("SegmentationTrainer initialized, but training is BLOCKED.")
        
    def train(self):
        """
        Execute the training pipeline.
        Currently blocked due to lack of dataset.
        """
        raise NotImplementedError(
            "Segmentation training is BLOCKED. Adequate segmentation data is unavailable."
        )
        
    def evaluate(self):
        """
        Evaluate the segmentation model.
        Currently blocked due to lack of dataset.
        """
        raise NotImplementedError(
            "Segmentation evaluation is BLOCKED. Adequate segmentation data is unavailable."
        )
