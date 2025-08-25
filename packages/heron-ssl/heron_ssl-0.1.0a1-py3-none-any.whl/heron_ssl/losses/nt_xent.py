import jax
import jax.numpy as jnp


def nt_xent_loss(projections: jnp.ndarray, temperature: float = 0.1) -> jnp.ndarray:
    projections = projections / jnp.linalg.norm(projections, axis=-1, keepdims=True)
    n = projections.shape[0]
    similarity_matrix = projections @ projections.T

    logits = similarity_matrix / temperature
    logits = logits - jnp.eye(n) * 1e9

    labels = jnp.arange(n)
    labels = jnp.where(labels % 2 == 0, labels + 1, labels - 1)

    loss = -jnp.sum(
        jax.nn.log_softmax(logits, axis=-1) * jax.nn.one_hot(labels, n),
        axis=-1,
    )
    return jnp.mean(loss)
