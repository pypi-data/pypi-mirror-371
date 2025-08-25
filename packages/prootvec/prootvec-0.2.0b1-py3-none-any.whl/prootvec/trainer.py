import numpy as np
from .losses import mse_loss
from .model import EmbeddingModel


class Trainer:
    """
    Entrenador básico de embeddings.
    Compatible con pares (token -> contexto).
    """

    def __init__(self, model: EmbeddingModel, lr: float = 0.05):
        if not isinstance(model, EmbeddingModel):
            raise TypeError("Se requiere un EmbeddingModel válido")
        if lr <= 0:
            raise ValueError("La tasa de aprendizaje debe ser positiva")

        self.model = model
        self.lr = lr

    def train_step(self, token_id: int, context_id: int) -> float:
        """
        Un paso de entrenamiento sobre un par (token, contexto).
        """
        try:
            token_vec = self.model.get_vector(token_id)
            context_vec = self.model.get_vector(context_id)
        except IndexError:
            return 0.0  # ignoramos pares inválidos

        # Pérdida (distancia entre vectores)
        loss = mse_loss(token_vec, context_vec)

        # Gradiente simple (token se acerca a contexto)
        grad = 2 * (token_vec - context_vec)
        self.model.update_vector(token_id, grad, self.lr)
        return loss

    def train_epoch(self, pairs, epochs: int = 5) -> None:
        """
        Entrena sobre múltiples pares de tokens.
        """
        if not pairs:
            raise ValueError("No hay pares de entrenamiento")

        for epoch in range(1, epochs + 1):
            total_loss = 0.0
            for t, c in pairs:
                total_loss += self.train_step(t, c)
            avg_loss = total_loss / len(pairs)
            print(f"📉 Época {epoch} - Pérdida: {avg_loss:.4f}")
