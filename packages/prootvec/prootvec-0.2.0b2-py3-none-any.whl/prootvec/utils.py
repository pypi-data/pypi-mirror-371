import json
import numpy as np
from typing import Tuple

from .model import EmbeddingModel
from .tokenizer import Tokenizer


def softmax(x: np.ndarray) -> np.ndarray:
    """
    Calcula softmax de un vector o matriz.
    """
    x = np.array(x, dtype=np.float64)
    # Estabilidad numérica
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / np.sum(e_x, axis=-1, keepdims=True)


def one_hot(index: int, size: int) -> np.ndarray:
    """
    Vector one-hot para un índice.
    """
    vec = np.zeros(size, dtype=np.float32)
    vec[index] = 1.0
    return vec


def save_model(path: str, model: EmbeddingModel, tokenizer: Tokenizer) -> None:
    """
    Guarda un modelo y un tokenizador en un archivo JSON.
    """
    if not hasattr(model, "to_dict"):
        raise AttributeError("El modelo debe implementar 'to_dict()'")
    if not hasattr(tokenizer, "to_dict"):
        raise AttributeError("El tokenizador debe implementar 'to_dict()'")

    data = {
        "model": model.to_dict(),
        "tokenizer": tokenizer.to_dict(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_model(path: str) -> Tuple[EmbeddingModel, Tokenizer]:
    """
    Carga un modelo y tokenizador desde un archivo JSON.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "model" not in data or "tokenizer" not in data:
        raise ValueError("El archivo no contiene los datos esperados")

    model = EmbeddingModel.from_dict(data["model"])
    tokenizer = Tokenizer()
    tokenizer.from_dict(data["tokenizer"])

    return model, tokenizer


def save_npz(path: str, model: EmbeddingModel) -> None:
    """
    Guarda los embeddings del modelo en formato NPZ comprimido.
    """
    if not hasattr(model, "embeddings"):
        raise AttributeError("El modelo debe tener un atributo 'embeddings'")
    np.savez_compressed(path, embeddings=model.embeddings)


def load_npz(path: str, model: EmbeddingModel) -> None:
    """
    Carga embeddings en un modelo desde un archivo NPZ.
    """
    if not hasattr(model, "embeddings"):
        raise AttributeError("El modelo debe tener un atributo 'embeddings'")

    data = np.load(path)
    if "embeddings" not in data:
        raise ValueError("El archivo NPZ no contiene 'embeddings'")

    arr = data["embeddings"]
    if arr.shape != model.embeddings.shape:
        raise ValueError(f"Shape de embeddings no coincide: {arr.shape} vs {model.embeddings.shape}")

    model.embeddings = arr
