# prootvec/__init__.py
# Inicializador del paquete prootvec
# Expone las clases y funciones principales

from .nltp import MLP, mse_loss, one_hot
from .reinforce import Reinforce
from .tokenizer import Tokenizer

# Entrenadores
from .trainer_micro import MicroTrainer   # Minimalista (basado en micrograd)
from .trainer import Trainer              # Masivo (numpy + batches grandes)

# Versión del paquete
__version__ = "0.1.0"

# Lo que se exporta al hacer "from prootvec import *"
__all__ = [
    "MLP",
    "mse_loss",
    "one_hot",
    "Reinforce",
    "Tokenizer",
    "Trainer",
    "MicroTrainer",
]
