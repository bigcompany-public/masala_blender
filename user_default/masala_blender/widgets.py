import sys
from pathlib import Path

import bpy
from masala.exporter import MasalaExporterWidget, get_exporters_config_from_path
from masala.gui.container import ContainerWidget
from masala.gui.utils import get_masala_exporter_icon
from qtpy.QtWidgets import QApplication


def show_exporter_widget(context: bpy.types.Context) -> ContainerWidget:
    # Get exporters config path from preferences
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    exporters_config = Path(addon_prefs.exporters_config)
    if not exporters_config.exists():
        raise FileNotFoundError(f"The python file does not exist : {exporters_config}")

    exporters = get_exporters_config_from_path(exporters_config)

    # Open Widget
    app = QApplication.instance() or QApplication(sys.argv)
    widget = MasalaExporterWidget(exporters)
    container = ContainerWidget(widget=widget, title="Masala Exporter", icon=get_masala_exporter_icon())
    container.show()
    return container
