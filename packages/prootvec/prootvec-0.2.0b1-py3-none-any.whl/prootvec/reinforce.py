import numpy as np
from .model import EmbeddingModel


class Reinforce:
    """
    Mini-refuerzo: ajusta vectores según similitud coseno.
    """

    def __init__(self, model: EmbeddingModel, lr: float = 0.01):
        if not isinstance(model, EmbeddingModel):
            raise TypeError("Se requiere un EmbeddingModel válido")
        if lr <= 0:
            raise ValueError("La tasa de aprendizaje debe ser positiva")

        self.model = model
        self.lr = lr

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcula similitud coseno entre dos vectores."""
        if a.shape != b.shape:
            raise ValueError("Vectores de distinta dimensión")
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9
        return float(np.dot(a, b) / denom)

    def reinforce_pair(self, token_id: int, context_id: int) -> float:
        """
        Refuerza la similitud entre dos vectores.
        Retorna la similitud antes del ajuste.
        """
        vec_a = self.model.get_vector(token_id)
        vec_b = self.model.get_vector(context_id)

        sim = self.cosine_similarity(vec_a, vec_b)
        grad = (vec_a - vec_b) * (1 - sim)

        self.model.update_vector(token_id, grad, self.lr)
        return sim
