# prootvec/model.py
from typing import Iterable, Tuple, Dict, Any, Optional, List
import numpy as np


class EmbeddingModel:
    """
    Modelo de embeddings ligero con NumPy.
    - Inicialización gaussiana
    - get_vector(s), update_vector(s)
    - normalización opcional
    - serialización (to_dict / from_dict)
    """

    def __init__(self, vocab_size: int, embed_dim: int = 8, seed: int = 42, init_scale: float = 0.1):
        if vocab_size <= 0:
            raise ValueError("vocab_size debe ser > 0")
        if embed_dim <= 0:
            raise ValueError("embed_dim debe ser > 0")

        rng = np.random.default_rng(seed)
        self.vocab_size = int(vocab_size)
        self.embed_dim = int(embed_dim)
        self.embeddings = rng.normal(0.0, init_scale, size=(self.vocab_size, self.embed_dim)).astype(float)

    # -----------------------------
    # Acceso
    # -----------------------------
    def get_vector(self, token_id: int) -> np.ndarray:
        token_id = int(token_id)
        if token_id < 0 or token_id >= self.vocab_size:
            raise IndexError(f"token_id {token_id} fuera de rango [0, {self.vocab_size-1}]")
        return self.embeddings[token_id]

    def get_vectors(self, token_ids: Iterable[int]) -> np.ndarray:
        idx = np.array(list(token_ids), dtype=int)
        if (idx < 0).any() or (idx >= self.vocab_size).any():
            raise IndexError("Algún token_id está fuera de rango.")
        return self.embeddings[idx]

    # -----------------------------
    # Actualización (SGD sencillo)
    # -----------------------------
    def update_vector(self, token_id: int, grad: np.ndarray, lr: float = 0.05) -> None:
        if grad.shape != (self.embed_dim,):
            raise ValueError(f"grad.shape debe ser {(self.embed_dim,)}, recibido {grad.shape}")
        self.embeddings[int(token_id)] -= float(lr) * grad

    def update_vectors(self, token_ids: Iterable[int], grads: np.ndarray, lr: float = 0.05) -> None:
        ids = np.array(list(token_ids), dtype=int)
        if grads.shape != (len(ids), self.embed_dim):
            raise ValueError(f"grads.shape debe ser {(len(ids), self.embed_dim)}, recibido {grads.shape}")
        self.embeddings[ids] -= float(lr) * grads

    # -----------------------------
    # Utilidades
    # -----------------------------
    def normalize(self, eps: float = 1e-9) -> None:
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True) + eps
        self.embeddings = self.embeddings / norms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vocab_size": self.vocab_size,
            "embed_dim": self.embed_dim,
            "embeddings": self.embeddings.tolist(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmbeddingModel":
        vs = int(data["vocab_size"])
        ed = int(data["embed_dim"])
        obj = cls(vs, ed)
        arr = np.array(data["embeddings"], dtype=float)
        if arr.shape != (vs, ed):
            raise ValueError(f"Embeddings con shape inválido: {arr.shape}, esperado {(vs, ed)}")
        obj.embeddings = arr
        return obj
