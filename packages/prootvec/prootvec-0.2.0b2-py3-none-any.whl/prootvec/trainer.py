# prootvec/trainer.py
from typing import List, Tuple, Iterable, Optional
import numpy as np
from tqdm import tqdm

from .losses import mse_loss
from .model import EmbeddingModel
from .tokenizer import Tokenizer


class Trainer:
    """
    Entrenador básico para embeddings.
    - Acepta corpus de texto o pares (ids).
    - Genera pares (ventana deslizante).
    - Usa SGD muy simple.
    """

    def __init__(self, model: EmbeddingModel, tokenizer: Tokenizer, lr: float = 0.05):
        if not isinstance(model, EmbeddingModel):
            raise TypeError("model debe ser EmbeddingModel")
        if not isinstance(tokenizer, Tokenizer):
            raise TypeError("tokenizer debe ser Tokenizer")
        if lr <= 0:
            raise ValueError("lr debe ser positivo")

        self.model = model
        self.tokenizer = tokenizer
        self.lr = lr

    # -----------------------------
    # Generación de pares
    # -----------------------------
    def make_pairs(
        self,
        corpus: Iterable[str],
        window: int = 2,
        dynamic: bool = True,
    ) -> List[Tuple[int, int]]:
        """
        Genera pares (token, contexto) a partir de un corpus.
        - window: tamaño de la ventana de contexto.
        - dynamic: si True, agrega tokens nuevos al vocab.
        """
        pairs: List[Tuple[int, int]] = []
        for sentence in corpus:
            ids = self.tokenizer.encode(sentence, add_new=dynamic)
            for i, center in enumerate(ids):
                for j in range(max(0, i - window), min(len(ids), i + window + 1)):
                    if i == j:
                        continue
                    pairs.append((center, ids[j]))
        return pairs

    # -----------------------------
    # Entrenamiento
    # -----------------------------
    def train_step(self, token_id: int, context_id: int) -> float:
        try:
            token_vec = self.model.get_vector(token_id)
            context_vec = self.model.get_vector(context_id)
        except IndexError:
            return 0.0

        loss = mse_loss(token_vec, context_vec)
        grad = 2 * (token_vec - context_vec)
        self.model.update_vector(token_id, grad, self.lr)
        return loss

    def train(
        self,
        corpus_or_pairs: Iterable,
        epochs: int = 5,
        window: int = 2,
        dynamic: bool = True,
        show_progress: bool = True,
    ) -> None:
        """
        Entrena embeddings a partir de corpus (texto) o pares (ids).
        """
        # detectar tipo
        if isinstance(next(iter(corpus_or_pairs)), str):
            pairs = self.make_pairs(corpus_or_pairs, window=window, dynamic=dynamic)
        else:
            pairs = list(corpus_or_pairs)

        if not pairs:
            raise ValueError("No hay pares para entrenar.")

        for epoch in range(1, epochs + 1):
            total_loss = 0.0
            iterator = tqdm(pairs, desc=f"Época {epoch}", disable=not show_progress)
            for t, c in iterator:
                total_loss += self.train_step(t, c)
            avg_loss = total_loss / len(pairs)
            print(f"📉 Época {epoch} - Pérdida promedio: {avg_loss:.4f}")
