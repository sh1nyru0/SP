from PyQt5.QtWidgets import QFileDialog
from qtpy import uic

from basemap_view import BaseMapView
from libs.share import MySignals, SI
from sactional_view import SactionalView

gms = MySignals()

class WinGraMagSetting:
    def __init__(self):
        self.ui = uic.loadUi("gramag_setting.ui")
        self.ui.setWindowTitle('重磁可视化')
        self.ui.setFixedSize(300, 100)
        self.ui.choose_file.clicked.connect(self.chooseFile)
        self.ui.btn_ok.clicked.connect(self.onOk)
        self.ui.btn_cancel.clicked.connect(self.onCancel)

    def chooseFile(self):
        self.filePath, _ = QFileDialog.getOpenFileName(
            self.ui,
            "选择你要处理的csv文件",
            SI.currentProject,
            "文件类型(*.csv)"
        )
        self.ui.file.setText(self.filePath)

    def onOk(self):
        if self.ui.type.currentText() == "剖面图":
            SI.sactionalViewWin = SactionalView()
            SI.sactionalViewWin.ui.show()


    def onOk(self):
        if self.ui.type.currentText() == "地图":
            SI.baseMapViewWin = BaseMapView()
            SI.baseMapViewWin.ui.show()

    def onCancel(self):
        self.ui.close()