from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit
from PyQt5.QtGui import QFont, QTextFormat, QPainter, QFontMetrics
from PyQt5.QtCore import QRect, Qt

from utils.lineNumberArea import LineNumberArea


class QCodeEditor(QPlainTextEdit):
    def __init__(self, display_line_numbers=True, highlight_current_line=True, syntax_high_lighter=None, *args):
        super(QCodeEditor, self).__init__(*args)

        self.setFont(QFont("Microsoft YaHei UI Light", 11))
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        # 设置制表符距离为 4 个空格的宽度
        font_metrics = QFontMetrics(self.font())
        self.setTabStopDistance(font_metrics.width(' ') * 4)

        self.DISPLAY_LINE_NUMBERS = display_line_numbers
        if display_line_numbers:
            self.number_bar = LineNumberArea(self)

        if highlight_current_line:
            self.currentLineNumber = None
            self.currentLineColor = self.palette().alternateBase()
            self.cursorPositionChanged.connect(self.highlight_current_line)

        if syntax_high_lighter is not None:
            self.highlighter = syntax_high_lighter(self.document())

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)

    def resizeEvent(self, *e):
        if self.DISPLAY_LINE_NUMBERS:
            cr = self.contentsRect()
            rec = QRect(0, 0, self.line_number_area_width(), cr.height())
            self.number_bar.setGeometry(rec)
        super(QCodeEditor, self).resizeEvent(*e)

    def highlight_current_line(self):
        new_current_line_number = self.textCursor().blockNumber()
        if new_current_line_number != self.currentLineNumber:
            self.currentLineNumber = new_current_line_number
            hi_selection = QTextEdit.ExtraSelection()
            hi_selection.format.setBackground(self.currentLineColor)
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()
            self.setExtraSelections([hi_selection])

    def line_number_area_width(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value //= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.number_bar.scroll(0, dy)
        else:
            self.number_bar.update(0, rect.y(), self.number_bar.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.number_bar)
        painter.fillRect(event.rect(), self.palette().base())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        height = self.fontMetrics().height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black if block_number == self.textCursor().blockNumber() else Qt.gray)
                painter.drawText(0, top, self.number_bar.width(), height, Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1