from PyQt5.QtWidgets import QMessageBox
from qtpy import uic
from libs.share import SI
class Preview_Data:
    def __init__(self, path):
        self.ui = uic.loadUi('preview_data.ui')
        self.ui.closeEvent = self.onCloseEvent
        self.path = path


    def onCloseEvent(self, event):
        choice = QMessageBox.question(
            self.ui,
            '确认',
            '要将本文件保存到原始文件中吗？')

        if choice == QMessageBox.Yes:
            SI.mainWin.savePreview(self.path)
        if choice == QMessageBox.No:
            return