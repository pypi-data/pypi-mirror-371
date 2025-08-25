import numpy as np


def mse_loss(pred: np.ndarray, target: np.ndarray) -> float:
    """
    Mean Squared Error (MSE).
    Calcula la pérdida promedio entre predicción y objetivo.
    """
    if pred.shape != target.shape:
        raise ValueError(f"Dimensiones incompatibles: {pred.shape} vs {target.shape}")
    return float(np.mean((pred - target) ** 2))
