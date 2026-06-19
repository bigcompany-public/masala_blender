import bpy

from .widgets import TestWidget


class MASALA_OT_PreferenceTest(bpy.types.Operator):
    bl_idname = "masala.preftest"
    bl_label = "Preference Test"

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        self.report({"INFO"}, f"Preference value: {addon_prefs.filepath}")
        return {"FINISHED"}


class MASALA_OT_Exporter(bpy.types.Operator):
    bl_idname = "masala.exporter"
    bl_label = "Exporter"
    bl_description = "Opens the Masala Exporter Tool"

    def execute(self, context):
        self.widget = TestWidget()
        self.widget.show()
        return {"RUNNING_MODAL"}


class MASALA_OT_Assembler(bpy.types.Operator):
    bl_idname = "masala.assembler"
    bl_label = "Assembler"

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        self.report({"INFO"}, f"Preference value: {addon_prefs.filepath}")
        return {"FINISHED"}
