import json
import numpy as np


def save_model(filepath: str, vocab: dict, embeddings: np.ndarray) -> None:
    """
    Guarda el vocabulario y embeddings en un archivo JSON.
    """
    data = {
        "vocab": vocab,
        "embeddings": embeddings.tolist()
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)
    print(f"✅ Modelo guardado en {filepath}")


def load_model(filepath: str):
    """
    Carga un modelo guardado desde JSON.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    vocab = data.get("vocab", {})
    embeddings = np.array(data.get("embeddings", []), dtype=float)
    if not vocab or embeddings.size == 0:
        raise ValueError("Archivo de modelo inválido o vacío")

    print(f"✅ Modelo cargado desde {filepath}")
    return vocab, embeddings
