
import numpy as np
import torch
from PIL import Image
from torchvision import models


class VisualFeatureExtractor:
    def __init__(self, device: str = ""):
        if not device:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
            
        # Load a pretrained ResNet50 model
        weights = models.ResNet50_Weights.DEFAULT
        model = models.resnet50(weights=weights)
        
        # Remove the final classification layer to get raw features (embeddings)
        self.model = torch.nn.Sequential(*(list(model.children())[:-1]))
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Standard ImageNet transforms
        self.preprocess = weights.transforms()

    def extract_features(self, image: Image.Image | torch.Tensor) -> np.ndarray:
        """
        Extracts visual features from a single image.
        """
        if isinstance(image, Image.Image):
            image = image.convert("RGB")
            input_tensor = self.preprocess(image)
        elif isinstance(image, torch.Tensor):
            input_tensor = image
        else:
            raise TypeError("Unsupported image format. Must be PIL Image or torch.Tensor.")
            
        # Add batch dimension
        if input_tensor.dim() == 3:
            input_batch = input_tensor.unsqueeze(0)
        else:
            input_batch = input_tensor
            
        input_batch = input_batch.to(self.device)
        
        with torch.no_grad():
            features = self.model(input_batch)
            
        # Flatten and normalize
        features = features.squeeze().cpu().numpy()
        
        if features.ndim == 1:
            features = features.reshape(1, -1)
            
        # L2 normalize features for cosine similarity
        norms = np.linalg.norm(features, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1.0, norms)
        features = features / norms
        
        return features.squeeze()

    def extract_batch(self, images: list[Image.Image]) -> np.ndarray:
        """
        Extracts visual features from a batch of images.
        """
        batch_tensors = []
        for img in images:
            img = img.convert("RGB")
            batch_tensors.append(self.preprocess(img))
            
        input_batch = torch.stack(batch_tensors).to(self.device)
        
        with torch.no_grad():
            features = self.model(input_batch)
            
        features = features.squeeze().cpu().numpy()
        if len(images) == 1 and features.ndim == 1:
            features = features.reshape(1, -1)
            
        norms = np.linalg.norm(features, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        features = features / norms
        
        return features
