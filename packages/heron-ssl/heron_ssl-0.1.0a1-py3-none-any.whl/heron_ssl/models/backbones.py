from typing import Protocol

import jax.numpy as jnp
from flax.linen import Module


class Backbone(Protocol):
    def __call__(self, x: jnp.ndarray, train: bool) -> jnp.ndarray: ...


class ResNet50(Module):
    def __call__(self, x: jnp.ndarray, train: bool = True) -> jnp.ndarray:
        raise NotImplementedError
