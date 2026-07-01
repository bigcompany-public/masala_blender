import sys
from pathlib import Path

import bpy

panel_scale_y = 1.5


class MASALA_PT_mainPanel(bpy.types.Panel):
    """Creates a Panel in the 3D_VIEW context"""

    bl_label = "Masala"
    bl_idname = "TOOLS_PT_masala"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Masala"

    def draw(self, context: bpy.types.Context):
        # extension path is added to sys.path at draw, because adding it in the __init__ file is not allowed
        extension_root_dir = Path(__file__).parent.parent
        if extension_root_dir.as_posix() not in sys.path:
            sys.path.append(extension_root_dir.as_posix())

        # Draw Masala Panel
        layout = self.layout
        assert isinstance(layout, bpy.types.UILayout)
        layout.scale_y = panel_scale_y
        row = layout.row()
        row.operator("masala.preftest")
        row = layout.row()
        row.operator("masala.reload")
        row = layout.row()
        row.operator("masala.exporter")
        row = layout.row()
        row.operator("masala.assembler")
