import importlib
import sys
from pathlib import Path

import bpy

from .widgets import show_exporter_widget


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
        self.widget = show_exporter_widget()
        return {"RUNNING_MODAL"}


class MASALA_OT_Assembler(bpy.types.Operator):
    bl_idname = "masala.assembler"
    bl_label = "Assembler"

    def execute(self, context):
        self.widget = TestWidget()
        self.widget.show()
        return {"RUNNING_MODAL"}


class MASALA_OT_Reload(bpy.types.Operator):
    bl_idname = "masala.reload"
    bl_label = "Reload"

    def execute(self, context):
        self.report({"INFO"}, "RELOAD")

        root_path = Path(__file__).parent

        modules_to_reload = []
        for module_name, module in list(sys.modules.items()):
            # Skip modules without file paths (built-ins, some packages like pywin32)
            module_file = getattr(module, "__file__", None)
            if not module_file:
                continue

            module_path = Path(module_file).as_posix()
            if module_path.startswith(root_path.as_posix()) or "/masala/" in module_path:
                modules_to_reload.append((module_name, module))
                continue

        for module_name, module in modules_to_reload:
            try:
                print(f"Reloading {module_name}")
                importlib.reload(module)
            except Exception as err:
                print(f"Failed to reload {module_name} ({err.__class__.__name__}: {err})")

        return {"FINISHED"}
