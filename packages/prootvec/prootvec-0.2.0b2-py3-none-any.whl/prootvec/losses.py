# prootvec/losses.py
import numpy as np


def mse_loss(pred: np.ndarray, target: np.ndarray) -> float:
    """
    Mean Squared Error.
    Ambos: shape (D,) o (N,D). Devuelve escalar.
    """
    pred = np.asarray(pred, dtype=float)
    target = np.asarray(target, dtype=float)
    if pred.shape != target.shape:
        raise ValueError(f"Dimensiones incompatibles: {pred.shape} vs {target.shape}")
    diff = pred - target
    return float(np.mean(diff * diff))


def cross_entropy_with_logits(logits: np.ndarray, target_onehot: np.ndarray) -> float:
    """
    Entropía cruzada estable:
    - logits: (V,) o (N,V)
    - target_onehot: (V,) o (N,V)
    """
    logits = np.asarray(logits, dtype=float)
    target = np.asarray(target_onehot, dtype=float)
    if logits.shape != target.shape:
        raise ValueError(f"Dimensiones incompatibles: {logits.shape} vs {target.shape}")

    if logits.ndim == 1:
        logits = logits[None, :]
        target = target[None, :]

    # log-softmax estable
    maxes = np.max(logits, axis=1, keepdims=True)
    lse = maxes + np.log(np.sum(np.exp(logits - maxes), axis=1, keepdims=True))
    log_probs = logits - lse
    # CE = -sum y*logp
    ce = -np.sum(target * log_probs, axis=1)
    return float(np.mean(ce))


def cosine_distance(a: np.ndarray, b: np.ndarray, eps: float = 1e-9) -> float:
    """
    Distancia coseno = 1 - similitud_coseno
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"Dimensiones incompatibles: {a.shape} vs {b.shape}")
    num = float(np.dot(a, b))
    den = float(np.linalg.norm(a) * np.linalg.norm(b)) + eps
    return 1.0 - (num / den)
