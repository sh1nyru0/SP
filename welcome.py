from PyQt5.QtGui import QColor
from qtpy import uic

from PyQt5.QtGui import QPainter, QPixmap, QFont
from PyQt5.QtCore import Qt

class Welcome:
    def __init__(self, connection=None, tabid=None, filename=None):
        self.ui = uic.loadUi('welcome.ui')
        w = self.ui.widget.width()
        h = self.ui.widget.height()
        pixmap = QPixmap("./images/welcome.png")
        painter = QPainter(pixmap)
        painter.end()

        self.ui.label.setPixmap(pixmap)
