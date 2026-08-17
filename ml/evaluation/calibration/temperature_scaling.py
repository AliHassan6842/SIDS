"""
Temperature scaling calibration tools for training/evaluation pipelines.
"""
import torch
from torch import nn, optim


class TemperatureScaler(nn.Module):
    """
    Temperature scaling for calibrating model outputs (logits).
    Finds the optimal temperature T using a validation set.
    """
    def __init__(self):
        super().__init__()
        # Initialize temperature to 1.5, a standard starting point for optimization
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)
        
    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Scale logits by the temperature.
        """
        # Expand temperature to match logits device/shape safely
        return logits / self.temperature
        
    def fit(self, logits: torch.Tensor, labels: torch.Tensor, lr: float = 0.01, max_iter: int = 100) -> float:
        """
        Tune the temperature parameter on a validation set using NLL loss.
        
        Args:
            logits: Pre-softmax logits from the model, shape (N, C)
            labels: True class labels, shape (N,)
            lr: Learning rate for LBFGS optimizer
            max_iter: Maximum number of iterations for LBFGS
            
        Returns:
            The optimized temperature value as a float
        """
        nll_criterion = nn.CrossEntropyLoss()
        optimizer = optim.LBFGS([self.temperature], lr=lr, max_iter=max_iter)
        
        def eval():
            optimizer.zero_grad()
            loss = nll_criterion(self.forward(logits), labels)
            loss.backward()
            return loss
            
        optimizer.step(eval)
        
        # Ensure temperature stays positive and reasonable
        with torch.no_grad():
            self.temperature.clamp_(min=1e-3, max=100.0)
            
        return self.temperature.item()

    def get_temperature(self) -> float:
        """Return the current temperature value."""
        return self.temperature.item()
