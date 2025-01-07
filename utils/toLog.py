from PyQt5.QtCore import QCoreApplication


class StreamToQPlainTextEdit:
    """将标准输出重定向到 QPlainTextEdit 的类"""
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, message):
        # 将消息追加到 QPlainTextEdit
        self.text_edit.appendPlainText(message.strip())
        self.text_edit.ensureCursorVisible()  # 自动滚动到底部
        QCoreApplication.processEvents()

    def flush(self):
        """为兼容性，flush 是必须的空实现"""
        pass