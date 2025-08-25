import numpy as np
from prootvec.utils import softmax


class Reinforce:
    """
    Implementación sencilla del algoritmo REINFORCE.
    Mantiene una política basada en preferencias y actualiza con recompensas.
    """

    def __init__(self, n_actions: int, lr: float = 0.01, seed: int = None):
        if n_actions <= 0:
            raise ValueError("El número de acciones debe ser mayor que 0")
        if lr <= 0:
            raise ValueError("La tasa de aprendizaje debe ser positiva")

        self.n_actions = n_actions
        self.lr = lr
        self.rng = np.random.default_rng(seed)

        # Inicializamos las preferencias de cada acción en 0
        self.preferences = np.zeros(n_actions, dtype=np.float32)

    def policy(self) -> np.ndarray:
        """
        Devuelve la distribución de probabilidad sobre las acciones.
        """
        return softmax(self.preferences)

    def sample_action(self) -> int:
        """
        Escoge una acción de acuerdo a la política actual.
        """
        probs = self.policy()
        return self.rng.choice(self.n_actions, p=probs)

    def update(self, action: int, reward: float) -> None:
        """
        Ajusta las preferencias según la acción tomada y la recompensa obtenida.
        """
        probs = self.policy()
        grad = -probs
        grad[action] += 1.0  # gradiente reforzado en la acción escogida

        # actualización estilo REINFORCE
        self.preferences += self.lr * reward * grad

    def train(self, env_fn, episodes: int = 100, verbose: bool = True):
        """
        Entrena el agente en un entorno (env_fn debe retornar reward por acción).
        Ejemplo de env_fn: lambda action: +1 si action==correcta else -1
        """
        rewards = []
        for ep in range(1, episodes + 1):
            action = self.sample_action()
            reward = env_fn(action)
            self.update(action, reward)
            rewards.append(reward)

            if verbose and ep % max(1, episodes // 10) == 0:
                avg = np.mean(rewards[-10:])
                print(f"📉 Episodio {ep}/{episodes} | Recompensa promedio (últimos 10): {avg:.3f}")

        return rewards
