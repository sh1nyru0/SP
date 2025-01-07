from PyQt5.QtCore import QRect
from PyQt5.QtGui import QFont,  QTextFormat
from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit
from utils1.lineNumberArea import LineNumberArea
class QCodeEditor(QPlainTextEdit):
    def __init__(self, display_line_numbers=True, highlight_current_line=True,
                 syntax_high_lighter=None, *args):
        """
        Parameters
        ----------
        display_line_numbers : bool
            switch on/off the presence of the lines number bar
        highlight_current_line : bool
            switch on/off the current line highlighting
        syntax_high_lighter : QSyntaxHighlighter
            should be inherited from QSyntaxHighlighter

        """
        super(QCodeEditor, self).__init__()

        self.setFont(QFont("Microsoft YaHei UI Light", 11))
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.DISPLAY_LINE_NUMBERS = display_line_numbers

        if display_line_numbers:
            self.number_bar = LineNumberArea(self)

        if highlight_current_line:
            self.currentLineNumber = None
            self.currentLineColor = self.palette().alternateBase()
            # self.currentLineColor = QColor("#e8e8e8")
            self.cursorPositionChanged.connect(self.highlight_current_line)

        if syntax_high_lighter is not None:  # add highlighter to text document
            self.highlighter = syntax_high_lighter(self.document())

    def resizeEvent(self, *e):
        """overload resizeEvent handler"""

        if self.DISPLAY_LINE_NUMBERS:  # resize LineNumberArea widget
            cr = self.contentsRect()
            rec = QRect(cr.left(), cr.top(), self.number_bar.get_width(), cr.height())
            self.number_bar.setGeometry(rec)

        QPlainTextEdit.resizeEvent(self, *e)

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

