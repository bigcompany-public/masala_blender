import sys

from masala.exporter import MasalaExporterWidget
from masala.gui.container import ContainerWidget
from qtpy.QtWidgets import QApplication


def show_exporter_widget() -> ContainerWidget:
    app = QApplication.instance() or QApplication(sys.argv)
    widget = MasalaExporterWidget([])
    container = ContainerWidget(widget=widget, title="Masala Exporter")
    container.show()
    return container
