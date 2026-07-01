from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

import bpy
from bpy.types import Collection, Material, Mesh, Object
from masala.api import Exporter
from masala.example.asset_blocks.materials import materials
from masala.example.codex import codex

from masala_blender.hierarchy import get_from_hierarchy, get_hierarchy_as_path

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


@dataclass
class MaterialSlotInfo:
    """Describes one material slot on a mesh object."""

    slot_index: int
    material_name: Optional[str]
    # Face indices that use this slot (empty = slot applies to whole mesh)
    face_indices: list[int] = field(default_factory=list)


@dataclass
class MeshMaterialMapping:
    """Full mapping for a single mesh object."""

    object_name: str
    mesh_data_name: str
    collection_path: str
    material_slots: list[MaterialSlotInfo] = field(default_factory=list)


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
        self._mesh_objects: list[Object] = []
        self._materials: list[Material] = []
        self._mappings: list[MeshMaterialMapping] = []

    def run(self) -> None:
        """Execute the full export pipeline."""
        # self.save_temp_scene()
        # self.pack_resources()
        self._mesh_objects = self.collect_mesh_objects()
        self._materials = self.list_materials(self._mesh_objects)
        self.export_materials(self._materials)
        self._mappings = self.build_mappings(self._mesh_objects)
        self.write_manifest(self._mappings)
        # print("Done")

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

    def collect_mesh_objects(self) -> list[Object]:
        """
        Return every MESH object that lives inside the static mesh collection

        The search is name-based: first locate the top-level collection whose
        name starts with ``ROOT_COLLECTION``, then find the child collection
        whose name starts with ``STATIC_MESH_COLLECTION``.
        """
        print("Collecting mesh objects")
        mesh_collection_path = codex.convs.blender_asset_meshes_collection.format(self.fields)
        mesh_collection = get_from_hierarchy(mesh_collection_path)
        assert isinstance(mesh_collection, Collection)

        mesh_objects: list[Object] = []
        self._collect_meshes_recursive(mesh_collection, mesh_objects)
        print(f"Found {len(mesh_objects)} mesh object(s).")
        return mesh_objects

    def list_materials(self, mesh_objects: list[Object]) -> list[Material]:
        """
        Return the deduplicated, name-sorted list of all materials that are
        referenced by at least one material slot across the given mesh objects.
        """
        print("Listing materials")
        seen: set[str] = set()
        materials: list[Material] = []

        for obj in mesh_objects:
            for slot in obj.material_slots:
                mat = slot.material
                if mat is not None and mat.name not in seen:
                    seen.add(mat.name)
                    materials.append(mat)

        materials.sort(key=lambda m: m.name)
        for mat in materials:
            print(f"Material: {mat.name}")
        print(f"Found {len(materials)} unique material(s).")
        return materials

    def export_materials(self, materials: list[Material]) -> None:
        """
        Write a .blend library file that contains ONLY the given materials
        (no meshes, objects, scenes, cameras, lights).

        The file can later be appended/linked into other projects via
        File → Append → <exported_materials.blend> → Material → <name>.
        """
        print("Exporting materials")
        if not materials:
            log.warning("No materials to export. skipping.")
            return

        mat_names = {m.name for m in materials}

        # bpy.data.libraries.write expects a set of data-block references.
        data_blocks: set[Material] = {m for m in bpy.data.materials if m.name in mat_names}

        bpy.data.libraries.write(
            str(self.material_blend_path),
            data_blocks,
            path_remap="RELATIVE",
            fake_user=True,
        )
        print(f"{len(data_blocks)} material(s) exported → {self.material_blend_path}")

    def build_mappings(self, mesh_objects: list[Object]) -> list[MeshMaterialMapping]:
        """
        For each mesh object, build a :class:`MeshMaterialMapping` that records:

        * which material occupies each slot
        * which polygon (face) indices are assigned to each slot

        If the mesh uses the same material for every face (no per-face
        assignment) the ``face_indices`` list is left empty.
        """
        print("Building mesh↔material manifest")
        mappings: list[MeshMaterialMapping] = []

        for obj in mesh_objects:
            mesh: Mesh = obj.data  # type: ignore[assignment]
            collection_path = get_hierarchy_as_path(mesh)

            # Build per-slot face-index lists
            slot_faces: dict[int, list[int]] = {i: [] for i in range(len(obj.material_slots))}
            for poly_index, poly in enumerate(mesh.polygons):
                slot_faces[poly.material_index].append(poly_index)

            # Determine whether all faces share the same slot
            all_same = len(slot_faces) <= 1

            slots: list[MaterialSlotInfo] = []
            for slot_index, slot in enumerate(obj.material_slots):
                face_list = [] if all_same else slot_faces.get(slot_index, [])
                slots.append(
                    MaterialSlotInfo(
                        slot_index=slot_index,
                        material_name=slot.material.name if slot.material else None,
                        face_indices=face_list,
                    )
                )

            mappings.append(
                MeshMaterialMapping(
                    object_name=obj.name,
                    mesh_data_name=mesh.name,
                    collection_path=collection_path,
                    material_slots=slots,
                )
            )

        return mappings

    def write_manifest(self, mappings: list[MeshMaterialMapping]) -> None:
        """
        Serialise the mesh↔material mappings to a pretty-printed JSON file.

        Schema (per mesh entry):
        ::

            {
              "object_name": "Cube.001",
              "mesh_data_name": "Cube",
              "collection_path": "myAsset/staticMesh",
              "material_slots": [
                {
                  "slot_index": 0,
                  "material_name": "M_Wood",
                  "face_indices": [0, 1, 4, 5]   // empty = whole mesh
                },
                ...
              ]
            }
        """
        payload = [asdict(m) for m in mappings]
        self.temp_manifest_path.write_text(json.dumps(payload, indent=4))

        print(
            f"Manifest written → {self.temp_manifest_path}",
        )

    @staticmethod
    def _find_collection(
        parent: Collection,
        name_prefix: str,
    ) -> Optional[Collection]:
        """
        Breadth-first search for the first collection whose name matches
        *name_prefix* exactly or starts with it (case-sensitive).
        Returns ``None`` if nothing is found.
        """
        queue: list[Collection] = list(parent.children)
        while queue:
            col = queue.pop(0)
            if col.name == name_prefix or col.name.startswith(name_prefix):
                return col
            queue.extend(col.children)
        return None

    @staticmethod
    def _collect_meshes_recursive(
        collection: Collection,
        result: list[Object],
    ) -> None:
        """Append all MESH objects from *collection* and its descendants."""
        for obj in collection.objects:
            if obj.type == "MESH":
                result.append(obj)
        for child in collection.children:
            MaterialExporter._collect_meshes_recursive(child, result)


def get_path() -> Path:
    path = bpy.data.filepath
    if not path:
        raise RuntimeError("Cannot extract current path. Please save your scene first")
    return Path(path)


def export(path: Path):
    exporter = MaterialExporter(path)
    exporter.run()


def meta(result: dict | None = None) -> dict:
    return {"hello": "world"}


material_exporter = Exporter(
    assetblock=materials,
    current_path_callback=get_path,
    export_callback=export,
    metadata_callback=meta,
)
