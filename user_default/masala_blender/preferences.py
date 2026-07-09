from pathlib import Path

import masala
from bpy.props import StringProperty
from bpy.types import AddonPreferences, Context


class MasalaPreferences(AddonPreferences):
    _package_name = __package__
    assert isinstance(_package_name, str)
    bl_idname = _package_name

    masala_root_dir = Path(masala.__file__).parent
    example_dir = masala_root_dir / "example_config_dir"
    default_exporters_module = example_dir / "exporters_config_mock.py"
    default_operators_module = example_dir / "operators_config_mock.py"

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
    recipes_config: StringProperty(
        name="Assembler Presets Directory",
        subtype="FILE_PATH",
        default=str(Path.home()),
    )

    def draw(self, context: Context):
        layout = self.layout
        layout.prop(self, "exporters_config")
        layout.prop(self, "operators_config")
        layout.prop(self, "recipes_config")
