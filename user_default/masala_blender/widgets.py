import importlib.util
import sys
from pathlib import Path

import bpy
from masala.api import Exporter
from masala.exporter import MasalaExporterWidget
from masala.gui.container import ContainerWidget
from qtpy.QtWidgets import QApplication


def show_exporter_widget(context: bpy.types.Context) -> ContainerWidget:
    sys.path.append(r"D:\gitWorkspace\masala_blender\user_default")

    # Get exporters config path from preferences
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    exporters_config = Path(addon_prefs.exporters_config)
    if not exporters_config.exists():
        raise FileNotFoundError(f"The python file does not exist : {exporters_config}")

    # Import config file as module
    module_name = "masalaconfig.exporters"
    spec = importlib.util.spec_from_file_location(module_name, exporters_config)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore

    # Get exporters
    if not hasattr(module, "exporters"):
        raise AttributeError(f'"exporters" variable is not set in {exporters_config}')
    exporters: list[Exporter] = getattr(module, "exporters")

    # Open Widget
    app = QApplication.instance() or QApplication(sys.argv)
    widget = MasalaExporterWidget(exporters)
    container = ContainerWidget(widget=widget, title="Masala Exporter")
    container.show()
    return container
