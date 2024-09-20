from PyQt5.QtGui import QColor
from qtpy import uic

from PyQt5.QtGui import QPainter, QPixmap, QFont
from PyQt5.QtCore import Qt

class Welcome:
    def __init__(self):
        self.ui = uic.loadUi('welcome.ui')
        w = self.ui.widget.width()
        h = self.ui.widget.height()
        pixmap = QPixmap("./images/welcome.png")
        painter = QPainter(pixmap)
        # font = QFont("黑体", pointSize=20)
        # painter.setFont(font)
        # painter.setPen(QColor(0, 0, 128))
        # painter.drawText(pixmap.rect(), Qt.AlignCenter, "欢迎使用！")
        painter.end()

        self.ui.label.setPixmap(pixmap)
