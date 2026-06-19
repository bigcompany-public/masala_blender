from bpy.props import StringProperty
from bpy.types import AddonPreferences, Context


class MasalaPreferences(AddonPreferences):
    _package_name = __package__
    assert isinstance(_package_name, str)
    bl_idname = _package_name

    filepath: StringProperty(
        name="Config Path",
        subtype="FILE_PATH",
    )

    def draw(self, context: Context):
        layout = self.layout
        layout.prop(self, "filepath")
