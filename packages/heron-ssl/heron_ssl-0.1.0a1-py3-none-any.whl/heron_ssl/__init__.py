import importlib
import logging

from .strategies import SimCLR
from .trainer import Trainer

_logger = logging.getLogger(__name__)

try:
    __version__ = importlib.metadata.version("template-python-library")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0-unknown"
    _logger.warning(
        "Could not determine package version using importlib.metadata. "
        "Is the library installed correctly?"
    )

__all__ = ["SimCLR", "Trainer"]
