import sys

from qtpy.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class TestWidget(QWidget):
    """
    This class represents a container widget for the subwidget to be inserted
    into.
    It works as a singleton, so the widget can be refreshed instead of creating
    multiple instances of the same widget
    """

    app = QApplication.instance() or QApplication(sys.argv)

    def __init__(self):
        super().__init__(parent=None)
        self.setup_ui()
        self.setup_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Hello World")
        layout.addWidget(label)

    def setup_signals(self):
        pass
