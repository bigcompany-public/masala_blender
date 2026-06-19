import bpy


def draw_menu(self, context: bpy.types.Context) -> None:
    layout = self.layout
    layout.operator("object.preftest")


def register() -> None:
    bpy.types.VIEW3D_MT_add.append(draw_menu)


def unregister() -> None:
    bpy.types.VIEW3D_MT_add.remove(draw_menu)
