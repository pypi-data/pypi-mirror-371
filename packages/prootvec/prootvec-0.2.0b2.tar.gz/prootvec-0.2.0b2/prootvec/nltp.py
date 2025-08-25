# prootvec/nltp.py
# MLP mínimo sobre micrograd (Value) para usar con one-hot de vocabulario.
# Objetivo: dado un token (one-hot), predecir su contexto (one-hot) vía MSE.

from typing import List
import random, math
from micrograd.engine import Value  # pip install micrograd


# --- Agregar tanh a Value si no existe ---
if not hasattr(Value, "tanh"):
    def tanh(self):
        # fórmula tanh(x) = (e^(2x) - 1) / (e^(2x) + 1)
        x = self.data
        t = (math.exp(2 * x) - 1) / (math.exp(2 * x) + 1)
        out = Value(t, (self,), 'tanh')

        def _backward():
            self.grad += (1 - t ** 2) * out.grad
        out._backward = _backward
        return out

    setattr(Value, "tanh", tanh)


def _rand(a=-0.1, b=0.1):
    return random.uniform(a, b)


class Neuron:
    def __init__(self, nin: int):
        # pesos + bias como Values para autograd
        self.w = [Value(_rand()) for _ in range(nin)]
        self.b = Value(0.0)

    def __call__(self, x: List[Value]) -> Value:
        # z = w·x + b
        act = sum((wi * xi for wi, xi in zip(self.w, x)), self.b)
        # activación tanh (suave, estable)
        return act.tanh()

    def parameters(self):
        return self.w + [self.b]


class Layer:
    def __init__(self, nin: int, nout: int):
        self.neurons = [Neuron(nin) for _ in range(nout)]

    def __call__(self, x: List[Value]) -> List[Value]:
        return [n(x) for n in self.neurons]

    def parameters(self):
        params = []
        for n in self.neurons:
            params.extend(n.parameters())
        return params


class MLP:
    def __init__(self, nin: int, nouts: List[int]):
        sz = [nin] + nouts
        self.layers = [Layer(sz[i], sz[i+1]) for i in range(len(nouts))]

    def __call__(self, x: List[Value]) -> List[Value]:
        for layer in self.layers:
            x = layer(x)
        return x  # lista de Values (logits activados con tanh)

    def parameters(self):
        params = []
        for l in self.layers:
            params.extend(l.parameters())
        return params


def mse_loss(pred: List[Value], target: List[float]) -> Value:
    # target es lista de floats (one-hot)
    assert len(pred) == len(target), "Dimensiones incompatibles en MSE"
    diffs = [(p - Value(t)) for p, t in zip(pred, target)]
    sq = [d * d for d in diffs]
    return sum(sq, Value(0.0)) * (1.0 / len(sq))


def one_hot(index: int, size: int) -> List[float]:
    v = [0.0] * size
    if 0 <= index < size:
        v[index] = 1.0
    return v
