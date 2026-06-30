from pathlib import Path

from bpy.props import StringProperty
from bpy.types import AddonPreferences, Context


class MasalaPreferences(AddonPreferences):
    _package_name = __package__
    assert isinstance(_package_name, str)
    bl_idname = _package_name

    example_dir = Path(__file__).parent / "example"
    default_assetblocks_module = example_dir / "assetblocks_config.py"
    default_exporters_module = example_dir / "exporters_config.py"
    default_operators_module = example_dir / "operators_config.py"

    assetblocks_config: StringProperty(
        name="AssetBlocks .py file",
        subtype="FILE_PATH",
        default=str(default_assetblocks_module),
    )
    exporters_config: StringProperty(
        name="Exporters .py file",
        subtype="FILE_PATH",
        default=str(default_exporters_module),
    )
    operators_config: StringProperty(
        name="Operators .py file",
        subtype="FILE_PATH",
        default=str(default_operators_module),
    )
    assembler_presets_dir: StringProperty(
        name="Assembler Presets Directory",
        subtype="FILE_PATH",
        default=str(Path.home()),
    )

    def draw(self, context: Context):
        layout = self.layout
        layout.prop(self, "assetblocks_config")
        layout.prop(self, "exporters_config")
        layout.prop(self, "operators_config")
        layout.prop(self, "assembler_presets_dir")
