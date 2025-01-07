from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QFont, QColor, QPainter
from PyQt5.QtWidgets import QWidget
class LineNumberArea(QWidget):
    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self.editor = editor
        self.editor.blockCountChanged.connect(self.update_width)
        self.editor.updateRequest.connect(self.update_contents)
        self.font = QFont()
        self.numberBarColor = QColor("#e8e8e8")

    def paintEvent(self, event):
        # Override paintEvent to draw the line numbers
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.numberBarColor)

        block = self.editor.firstVisibleBlock()

        # Iterate over all visible text blocks in the document.
        while block.isValid():
            block_number = block.blockNumber()
            block_top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()

            # Check if the position of the block is outside the visible area.
            if not block.isVisible() or block_top >= event.rect().bottom():
                break

            # We want the line number for the selected line to be bold.
            if block_number == self.editor.textCursor().blockNumber():
                self.font.setBold(True)
                painter.setPen(QColor("#000000"))
            else:
                self.font.setBold(False)
                painter.setPen(QColor("#717171"))
            painter.setFont(self.font)

            # Draw the line number right justified at the position of the line.
            paint_rect = QRect(0, int(block_top), self.width(), self.editor.fontMetrics().height())
            painter.drawText(paint_rect, Qt.AlignRight, str(block_number + 1))

            block = block.next()

        painter.end()

        QWidget.paintEvent(self, event)

    # 根据文档的总行数来计算宽度
    def get_width(self):
        count = self.editor.blockCount()
        width = self.fontMetrics().width(str(count)) + 10
        return width

    # 设置宽度
    def update_width(self):
        width = self.get_width()
        if self.width() != width:
            self.setFixedWidth(width)
            self.editor.setViewportMargins(width, 0, 0, 0);

    # 更行内容
    def update_contents(self, rect, scroll):
        if scroll:
            self.scroll(0, scroll)
        else:
            self.update(0, rect.y(), self.width(), rect.height())

        if rect.contains(self.editor.viewport().rect()):
            font_size = self.editor.currentCharFormat().font().pointSize()
            self.font.setPointSize(font_size)
            self.font.setStyle(QFont.StyleNormal)
            self.update_width()

