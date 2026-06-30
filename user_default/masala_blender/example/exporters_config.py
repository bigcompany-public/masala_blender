from .exporters.material_exporter import material_exporter
from .exporters.static_mesh_exporter import static_mesh_exporter

exporters = [
    static_mesh_exporter,
    material_exporter,
]
