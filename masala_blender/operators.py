import bpy


class PreferenceTestOperator(bpy.types.Operator):
    bl_idname = "object.preftest"
    bl_label = "Preference Test"

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        print(addon_prefs.filepath)
        self.report({"INFO"}, f"Preference value: {addon_prefs.filepath}")
        return {"FINISHED"}
