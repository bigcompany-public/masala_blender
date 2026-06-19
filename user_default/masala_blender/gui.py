import bpy

panel_scale_x = 1.3
panel_scale_y = 1.3


class MASALA_PT_mainPanel(bpy.types.Panel):
    """Creates a Panel in the 3D_VIEW context"""

    bl_label = "Masala"
    bl_idname = "TOOLS_PT_masala"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Masala"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        assert isinstance(layout, bpy.types.UILayout)
        layout.scale_x = panel_scale_x
        layout.scale_y = panel_scale_y
        row = layout.row()
        row.operator("masala.preftest")
        row = layout.row()
        row.operator("masala.reload")
        row = layout.row()
        row.operator("masala.exporter")
        row = layout.row()
        row.operator("masala.assembler")
