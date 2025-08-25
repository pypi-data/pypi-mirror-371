# prootvec/tokenizer.py
from typing import List, Dict, Iterable, Tuple, Optional
import regex as re

_SPECIALS = ["<PAD>", "<UNK>", "<BOS>", "<EOS>"]

class Tokenizer:
    """
    Tokenizador básico y robusto, con:
    - Vocab dinámico (add_token / add_new=True en encode)
    - Tokens especiales: <PAD>, <UNK>, <BOS>, <EOS>
    - Soporte n-gram (1 o 2)
    """

    def __init__(self, lowercase: bool = True, keep_numbers: bool = True, min_freq: int = 1):
        self.lowercase = lowercase
        self.keep_numbers = keep_numbers
        self.min_freq = min_freq  # 🔑 ahora se guarda como atributo
        self.vocab: Dict[str, int] = {}
        self.inverse_vocab: Dict[int, str] = {}
        self._init_specials()

    # -----------------------------
    # Vocab
    # -----------------------------
    def _init_specials(self):
        self.vocab.clear()
        for sp in _SPECIALS:
            self.vocab[sp] = len(self.vocab)
        self._sync_inverse()

    def _sync_inverse(self):
        self.inverse_vocab = {i: w for w, i in self.vocab.items()}

    @property
    def pad_id(self) -> int:
        return self.vocab["<PAD>"]

    @property
    def unk_id(self) -> int:
        return self.vocab["<UNK>"]

    def add_token(self, token: str) -> int:
        """Agrega un token al vocabulario si no existe y devuelve su id."""
        if token not in self.vocab:
            self.vocab[token] = len(self.vocab)
            self.inverse_vocab[self.vocab[token]] = token
        return self.vocab[token]

    def add_tokens(self, tokens: Iterable[str]) -> None:
        for t in tokens:
            self.add_token(t)

    def has_token(self, token: str) -> bool:
        return token in self.vocab

    # -----------------------------
    # Construcción de vocabulario
    # -----------------------------
    def build_vocab(
        self,
        texts: Iterable[str],
        min_freq: Optional[int] = None,
        include_bigrams: bool = False
    ) -> Dict[str, int]:
        """
        Construye vocab con min_freq (del argumento o del __init__)
        y opcionalmente con bigramas.
        """
        if not texts:
            raise ValueError("Se requiere un iterable de textos no vacío.")

        # Usa el min_freq de init si no se pasa otro
        if min_freq is None:
            min_freq = self.min_freq

        # reinicia (pero mantiene especiales)
        self._init_specials()

        freq: Dict[str, int] = {}
        for text in texts:
            toks = list(self._tokenize(text))
            for tok in toks:
                freq[tok] = freq.get(tok, 0) + 1
            if include_bigrams:
                for a, b in self._bigrams(toks):
                    bg = f"{a}_{b}"
                    freq[bg] = freq.get(bg, 0) + 1

        for token, c in sorted(freq.items()):
            if c >= min_freq:
                self.add_token(token)

        self._sync_inverse()
        return self.vocab

    # -----------------------------
    # Tokenización y codificación
    # -----------------------------
    def _tokenize(self, text: str) -> Iterable[str]:
        if text is None:
            text = ""
        s = str(text)
        if self.lowercase:
            s = s.lower()
        # separa palabras básicas (mejorable)
        return re.findall(r"\w+", s)

    def _bigrams(self, tokens: List[str]) -> Iterable[Tuple[str, str]]:
        for i in range(len(tokens) - 1):
            yield tokens[i], tokens[i + 1]
        # letras (unicode) y números opcionalmente
        # \p{L} = letra unicode; \p{N} = número
        if self.keep_numbers:
            pattern = r"\p{L}+\p{N}*|\p{N}+"
        else:
            pattern = r"\p{L}+"

        for m in re.finditer(pattern, s):
            yield m.group(0)

    def _bigrams(self, toks: List[str]) -> Iterable[Tuple[str, str]]:
        for i in range(len(toks) - 1):
            yield toks[i], toks[i + 1]

    def encode(
        self,
        text: str,
        ngram: int = 1,
        add_new: bool = False,
        add_bos_eos: bool = False
    ) -> List[int]:
        """
        Convierte texto a ids.
        - ngram: 1 (unigramas) o 2 (bigramas).
        - add_new=True: tokens OOV se añaden al vocab dinámicamente.
        - add_bos_eos=True: antepone <BOS> y añade <EOS>.
        """
        if ngram not in (1, 2):
            raise ValueError("ngram debe ser 1 o 2")

        ids: List[int] = []
        if add_bos_eos:
            ids.append(self.vocab["<BOS>"])

        toks = list(self._tokenize(text))
        units: List[str]
        if ngram == 1:
            units = toks
        else:
            units = [f"{a}_{b}" for a, b in self._bigrams(toks)]

        for u in units:
            if u in self.vocab:
                ids.append(self.vocab[u])
            elif add_new:
                ids.append(self.add_token(u))
            else:
                ids.append(self.unk_id)

        if add_bos_eos:
            ids.append(self.vocab["<EOS>"])
        return ids

    def batch_encode(
        self,
        texts: Iterable[str],
        ngram: int = 1,
        add_new: bool = False,
        add_bos_eos: bool = False
    ) -> List[List[int]]:
        return [self.encode(t, ngram=ngram, add_new=add_new, add_bos_eos=add_bos_eos) for t in texts]

    def decode(self, ids: List[int], skip_specials: bool = True) -> str:
        toks: List[str] = []
        for i in ids:
            tok = self.inverse_vocab.get(i, "<UNK>")
            if skip_specials and tok in _SPECIALS:
                continue
            toks.append(tok)
        # si hay bigramas codificados con "_", no intentamos separarlos aquí
        return " ".join(toks)

    # -----------------------------
    # Serialización
    # -----------------------------
    def to_dict(self) -> Dict[str, Dict[str, int]]:
        return {"vocab": self.vocab}

    def from_dict(self, data: Dict[str, Dict[str, int]]) -> None:
        vocab = data.get("vocab")
        if not isinstance(vocab, dict) or not vocab:
            raise ValueError("Estructura de vocabulario inválida.")
        self.vocab = dict(vocab)
        self._sync_inverse()
