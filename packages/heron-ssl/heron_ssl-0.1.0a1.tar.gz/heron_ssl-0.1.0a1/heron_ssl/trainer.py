from typing import Any

import optax


class Trainer:
    def __init__(self, strategy: Any, optimizer: optax.GradientTransformation):
        self.strategy = strategy
        self.optimizer = optimizer

    def fit(self, train_dataset: Any) -> Any:
        raise NotImplementedError
