import sys

from masala.example.function_node_registry import function_node_descriptions
from masala.example.registry import registry
from masala.nodegraph import AssemblerGraph
from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class TestWidget(QWidget):
    app = QApplication.instance() or QApplication(sys.argv)

    def __init__(self):
        super().__init__(parent=None)
        self.setup_ui()
        self.setup_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Hello World")
        layout.addWidget(label)

        graph_widget = AssemblerGraph(registry, function_node_descriptions)
        layout.addWidget(graph_widget.widget)

    def setup_signals(self):
        pass
