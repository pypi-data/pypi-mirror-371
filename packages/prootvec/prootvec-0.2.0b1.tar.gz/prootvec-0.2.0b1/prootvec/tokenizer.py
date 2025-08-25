import re
from typing import List, Dict


class Tokenizer:
    """
    Tokenizador básico.
    Convierte texto en tokens numéricos y viceversa.
    """

    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}

    def build_vocab(self, texts: List[str]) -> Dict[str, int]:
        """
        Construye un vocabulario a partir de una lista de textos.
        """
        if not texts or not isinstance(texts, list):
            raise ValueError("Se requiere una lista de textos no vacía")

        words = []
        for text in texts:
            text = str(text).lower()
            words.extend(re.findall(r"\w+", text))

        unique_words = sorted(set(words))
        self.vocab = {w: i for i, w in enumerate(unique_words)}
        self.inverse_vocab = {i: w for w, i in self.vocab.items()}
        return self.vocab

    def encode(self, text: str) -> List[int]:
        """
        Convierte texto en tokens numéricos.
        """
        if not self.vocab:
            raise RuntimeError("Vocabulario no construido. Ejecuta build_vocab primero.")

        tokens = []
        for word in re.findall(r"\w+", text.lower()):
            if word in self.vocab:
                tokens.append(self.vocab[word])
            else:
                # Si no existe, lo ignoramos (puede cambiarse por <UNK>)
                continue
        return tokens

    def decode(self, tokens: List[int]) -> str:
        """
        Convierte tokens numéricos en texto.
        """
        if not self.inverse_vocab:
            raise RuntimeError("Vocabulario no construido.")
        return " ".join(self.inverse_vocab.get(t, "<UNK>") for t in tokens)
