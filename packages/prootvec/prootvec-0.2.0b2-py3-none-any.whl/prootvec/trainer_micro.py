# prootvec/trainer_micro.py
# Entrena un MLP (NLTP) para predecir el contexto dado el token central.
from typing import List, Tuple
from tqdm import trange  # pip install tqdm
from micrograd.engine import Value
from .nltp import MLP, mse_loss, one_hot

class MicroTrainer:
    """
    Entrenamiento tipo skip-gram minimalista usando un MLP:
    input: one-hot(center) -> MLP -> salida (aprox. one-hot(context)).
    Pérdida: MSE entre salida y one-hot context.
    """

    def __init__(self, vocab_size: int, hidden: int = 16, lr: float = 0.05, seed: int = 42):
        if vocab_size <= 0:
            raise ValueError("vocab_size > 0 requerido")
        if hidden <= 0:
            raise ValueError("hidden > 0 requerido")
        if lr <= 0:
            raise ValueError("lr > 0 requerido")
        import random
        random.seed(seed)

        self.vocab_size = vocab_size
        self.model = MLP(nin=vocab_size, nouts=[hidden, vocab_size])
        self.lr = lr

    def _to_values(self, onehot: List[float]) -> List[Value]:
        # Convierte floats a micrograd Values (no requieren grad explícito, se propaga)
        return [Value(x) for x in onehot]

    def train(self, pairs: List[Tuple[int, int]], epochs: int = 5, progress: bool = True) -> List[float]:
        if not pairs:
            raise ValueError("Lista de pares vacía")

        losses = []
        rng = trange(epochs, desc="Entrenando", ncols=80) if progress else range(epochs)
        for _ in rng:
            total = 0.0
            # SGD sobre todos los pares
            for center, context in pairs:
                x = self._to_values(one_hot(center, self.vocab_size))
                y_true = one_hot(context, self.vocab_size)

                # forward
                y_pred = self.model(x)
                loss = mse_loss(y_pred, y_true)

                # backward
                for p in self.model.parameters():
                    p.grad = 0.0
                loss.backward()

                # update
                for p in self.model.parameters():
                    p.data += -self.lr * p.grad

                total += loss.data

            losses.append(total / len(pairs))
            if progress:
                rng.set_postfix_str(f"loss={losses[-1]:.4f}")
        return losses

    def predict_logits(self, token_id: int) -> List[float]:
        x = self._to_values(one_hot(token_id, self.vocab_size))
        y = self.model(x)
        return [v.data for v in y]

    def most_likely(self, token_id: int, topk: int = 5) -> List[Tuple[int, float]]:
        logits = self.predict_logits(token_id)
        # como usamos tanh, son “scores” en [-1,1]; top-k por score
        idx = list(range(self.vocab_size))
        idx.sort(key=lambda i: logits[i], reverse=True)
        return [(i, logits[i]) for i in idx[:topk]]
