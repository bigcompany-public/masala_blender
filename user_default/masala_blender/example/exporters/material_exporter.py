from __future__ import annotations

import logging
from pathlib import Path

import bpy
from bpy.types import Collection, Material, Mesh, Object
from masala.api import Exporter
from masala.example.assetblocks_dir.materials import materials
from masala.example.codex import codex

from masala_blender.hierarchy import get_from_hierarchy

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


class MaterialExporter:
    """
    Orchestrates material discovery, export, and manifest generation for
    all mesh objects found under the  myAsset/staticMesh  collection hierarchy.
    """

    def __init__(
        self,
        output_path: str | Path,
    ) -> None:
        self.current_path = get_path()
        self.fields = codex.get_fields(self.current_path)
        self.temp_dir = self.current_path.parent / "temp"
        self.temp_blend_path = self.temp_dir / self.current_path.name
        self.temp_manifest_path = self.temp_blend_path.with_suffix(".json")
        self.material_blend_path = Path(output_path)
        self.material_data: list[dict] = []
        self.materials: list[Material]

    def run(self) -> list[dict]:
        """Execute the full export pipeline."""
        self.save_temp_scene()
        self.pack_resources()
        self.extract_mesh_to_material_data()
        self.export_materials()
        return self.material_data

    def extract_mesh_to_material_data(self):
        mesh_collection_path = Path(codex.convs.blender_asset_meshes_collection.format(self.fields))
        mesh_collection = get_from_hierarchy(mesh_collection_path)
        assert isinstance(mesh_collection, Collection)

        material_data: list[dict] = []
        materials: list[Material] = []
        self._recursively_explore_hierarchy(mesh_collection, mesh_collection_path, material_data, materials)
        self.material_data = sorted(material_data, key=lambda data: data["mesh_path"])
        self.materials = sorted(materials, key=lambda mtl: mtl.name)

    def _recursively_explore_hierarchy(
        self, item: Collection | Object, current_path: Path, material_data: list, materials: list
    ):
        # If Collection, dig deeper into the collections child collections and child objects
        if isinstance(item, Collection):
            for obj in item.objects:
                self._recursively_explore_hierarchy(obj, current_path.joinpath(obj.name), material_data, materials)
            for col in item.children:
                self._recursively_explore_hierarchy(col, current_path.joinpath(col.name), material_data, materials)

        # if object, extract data from the mesh's material slots
        elif isinstance(item, Object):
            mesh_data = {}

            # Get mesh
            obj = item
            mesh = item.data
            assert isinstance(mesh, Mesh)
            path = current_path.joinpath(mesh.name)
            mesh_data["mesh_path"] = path.as_posix()
            mesh_data["material_slots"] = []

            # Iterate over material slots
            for mtl_slot in obj.material_slots:
                if not mtl_slot.material:
                    continue
                mtl_slot_data = {}
                mtl_slot_data["index"] = mtl_slot.slot_index
                mtl_slot_data["material"] = mtl_slot.material.name
                mtl_slot_data["polygons"] = []

                # Register material
                if mtl_slot.material not in materials:
                    materials.append(mtl_slot.material)

                # Iterate over polygons
                for polygon in mesh.polygons:
                    if polygon.material_index == mtl_slot.slot_index:
                        mtl_slot_data["polygons"].append(polygon.index)

                mesh_data["material_slots"].append(mtl_slot_data)

            material_data.append(mesh_data)

    def save_temp_scene(self) -> None:
        """
        Save the current .blend file to a temporary path so the original is
        never overwritten and subsequent operations work on a known-good copy.
        """
        print("Saving temporary scene")
        self.temp_blend_path.parent.mkdir(exist_ok=True, parents=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(self.temp_blend_path), copy=True)
        print("Temporary scene saved → %s", self.temp_blend_path)

    def pack_resources(self) -> None:
        """
        Pack all external resources (textures, fonts, sounds, volumes) into
        the .blend data-block so the file is self-contained.
        """
        print("Packing external resources")
        bpy.ops.file.pack_all()
        print("All external resources packed.")

    def export_materials(self) -> None:
        """
        Write a .blend library file that contains ONLY the given materials
        (no meshes, objects, scenes, cameras, lights).

        The file can later be appended/linked into other projects via
        File → Append → <exported_materials.blend> → Material → <name>.
        """
        print("Exporting materials")
        if not self.materials:
            log.warning("No materials to export. skipping.")
            return

        bpy.data.libraries.write(
            str(self.material_blend_path),
            set(self.materials),
            path_remap="RELATIVE",
            fake_user=True,
        )
        print(f"{len(self.materials)} material(s) exported → {self.material_blend_path}")


def get_path() -> Path:
    path = bpy.data.filepath
    if not path:
        raise RuntimeError("Cannot extract current path. Please save your scene first")
    return Path(path)


def export(path: Path) -> dict:
    exporter = MaterialExporter(path)
    return {"material_mapping": exporter.run()}


material_exporter = Exporter(
    assetblock=materials,
    current_path_callback=get_path,
    export_callback=export,
)
