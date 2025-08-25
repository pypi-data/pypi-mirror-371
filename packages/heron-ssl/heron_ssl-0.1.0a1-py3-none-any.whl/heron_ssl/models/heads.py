from collections.abc import Sequence

import jax.numpy as jnp
from flax import linen as nn


class ProjectionHead(nn.Module):
    hidden_dims: Sequence[int]
    output_dim: int

    @nn.compact
    def __call__(self, x: jnp.ndarray) -> jnp.ndarray:
        for dim in self.hidden_dims:
            x = nn.Dense(features=dim)(x)
            x = nn.relu(x)
        x = nn.Dense(features=self.output_dim)(x)
        return x
