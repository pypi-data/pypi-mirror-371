import numpy as np


class EmbeddingModel:
    """
    Modelo de embeddings súper ligero.
    """

    def __init__(self, vocab_size: int, embed_dim: int = 8, seed: int = 42):
        if vocab_size <= 0:
            raise ValueError("El tamaño del vocabulario debe ser mayor a 0")
        if embed_dim <= 0:
            raise ValueError("La dimensión del embedding debe ser positiva")

        np.random.seed(seed)
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.embeddings = np.random.randn(vocab_size, embed_dim) * 0.1

    def get_vector(self, token_id: int) -> np.ndarray:
        if token_id < 0 or token_id >= self.vocab_size:
            raise IndexError(f"Token_id {token_id} fuera de rango (0-{self.vocab_size-1})")
        return self.embeddings[token_id]

    def update_vector(self, token_id: int, grad: np.ndarray, lr: float = 0.01):
        if grad.shape != (self.embed_dim,):
            raise ValueError(f"Gradiente inválido. Esperado {(self.embed_dim,)}, recibido {grad.shape}")
        self.embeddings[token_id] -= lr * grad
