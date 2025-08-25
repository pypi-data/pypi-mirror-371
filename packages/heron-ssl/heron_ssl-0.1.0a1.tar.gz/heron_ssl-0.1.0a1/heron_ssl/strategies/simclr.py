from flax.struct import dataclass

from heron_ssl.models.backbones import Backbone
from heron_ssl.models.heads import ProjectionHead


@dataclass
class SimCLR:
    backbone: Backbone
    projector: ProjectionHead
