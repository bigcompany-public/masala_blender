from masala.api import AssetBlockRegistry
from masala.example.codex import codex

from .assetblocks.materials import materials
from .assetblocks.rig import rig
from .assetblocks.staticmesh import static_mesh

assetblocks = [
    static_mesh,
    materials,
    rig,
]

assetblock_registry = AssetBlockRegistry(assetblocks, codex)
