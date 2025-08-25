<div align="center">
  <picture>
    <img alt="Heron Logo" src="logo.svg" height="25%" width="25%">
  </picture>
<br>

<h2>Heron</h2>

[![Tests](https://img.shields.io/github/actions/workflow/status/habedi/heron/tests.yml?label=tests&style=flat&labelColor=333333&logo=github&logoColor=white)](https://github.com/habedi/heron/actions/workflows/tests.yml)
[![Code Coverage](https://img.shields.io/codecov/c/github/habedi/heron?style=flat&label=coverage&labelColor=333333&logo=codecov&logoColor=white)](https://codecov.io/gh/habedi/heron)
[![Code Quality](https://img.shields.io/codefactor/grade/github/habedi/heron?style=flat&label=code%20quality&labelColor=333333&logo=codefactor&logoColor=white)](https://www.codefactor.io/repository/github/habedi/heron)
[![PyPI Version](https://img.shields.io/pypi/v/heron.svg?style=flat&label=pypi&labelColor=333333&logo=pypi&logoColor=white&color=3775a9)](https://pypi.org/project/heron-ssl/)
[![Python Version](https://img.shields.io/badge/python-%3E=3.10-3776ab?style=flat&labelColor=333333&logo=python&logoColor=white)](https://github.com/habedi/heron)
[![Documentation](https://img.shields.io/badge/docs-latest-8ca0d7?style=flat&labelColor=333333&logo=read-the-docs&logoColor=white)](https://github.com/habedi/heron/blob/main/docs)
[![License](https://img.shields.io/badge/license-MIT-00acc1?style=flat&labelColor=333333&logo=open-source-initiative&logoColor=white)](https://github.com/habedi/heron/blob/main/LICENSE)

</div>

---

Heron is a high-level self-supervised learning (SSL) library built on JAX, Flax, and Optax.
It provides high-level abstractions to simplify the process of training and experimenting with SSL algorithms,
allowing you to focus on the model and data, not the boilerplate.

Heron aims to be modular and extensible, with clear separation between models, loss functions, data augmentations,
and training strategies.

### Core Features

- **High-Level Trainer API**: A simple `Trainer` class that abstracts away the complexities of JAX's functional
  paradigm, including `jit`, `pmap`, and state management.
- **Modular Design**: Easily mix and match backbones, heads, loss functions, and augmentation pipelines.
- **SSL Strategies**: Pre-packaged implementations of popular SSL algorithms.
- **Performance**: Built on JAX and Flax to leverage hardware acceleration on GPUs and TPUs.

---

### Feature Roadmap

    -   [x] Establish core abstractions (`Trainer`, `Backbone`, `ProjectionHead`).
    -   [x] Implement **SimCLR** as the first end-to-end strategy.
    -   [ ] Implement a robust data augmentation pipeline for contrastive learning.
    -   [ ] Initial PyPI release.
    -   [ ] Implement **BYOL** and **SimSiam** (non-contrastive methods).
    -   [ ] Add logic for momentum encoders (teacher-student models).
    -   [ ] Refine `TrainState` management and checkpointing.
    -   [ ] Implement **DINO** and **MoCo v3**.
    -   [ ] Add Vision Transformer (ViT) backbones.
    -   [ ] Implement teacher-student centering and sharpening.
    -   [ ] Masked Image Modeling strategies (e.g., **MAE**).
    -   [ ] Integration with Hugging Face models and datasets.
    -   [ ] Comprehensive documentation and tutorials.

---

### Installation

```shell
pip install heron-ssl
````

### Quick Start

Here is a conceptual example of how to use the `Trainer` API.

```python
import heron_ssl as ssl
import tensorflow_datasets as tfds
import optax

# 1. Load a dataset
dataset = tfds.load('cifar10', split='train')

# 2. Define the model and SSL strategy
strategy = ssl.strategies.SimCLR(
    backbone=ssl.models.ResNet50(),
    projector=ssl.models.ProjectionHead(hidden_dims=[2048], output_dim=128),
)

# 3. Configure and run the trainer
trainer = ssl.Trainer(
    strategy=strategy,
    optimizer=optax.adam(1e-3),
)

# 4. Start training
trained_backbone_params = trainer.fit(dataset)
```

### Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

### License

Heron is licensed under the MIT License ([LICENSE](LICENSE)).

### Acknowledgements

* Logo is from [SVG Repo](https://www.svgrepo.com/svg/452899/heron).
