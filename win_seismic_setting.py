from PyQt5.QtWidgets import QFileDialog
from qtpy import uic

from libs.share import MySignals, SI
from seismic_slice_setting import SeismicSliceSetting
from spectrum_analysis import SpectrumAnalysis
from variable_density_map import VariableDensityMap

gms = MySignals()


class WinSeismicSetting:
    def __init__(self):
        self.ui = uic.loadUi("seismic_setting.ui")
        self.ui.setWindowTitle('地震可视化')
        self.ui.setFixedSize(300, 100) # 固定窗口大小
        self.ui.choose_file.clicked.connect(self.chooseFile)
        self.ui.btn_ok.clicked.connect(self.onOk)
        self.ui.btn_cancel.clicked.connect(self.onCancel)

    def chooseFile(self):
        self.filePath, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择你要处理的sgy文件",  # 标题
            SI.currentProject,  # 起始目录
            # "文件类型 (*.sgy)"  # 选择类型过滤项，过滤内容在括号中
            "文件类型 (*.sgy)"  # 选择类型过滤项，过滤内容在括号中
        )
        self.ui.file.setText(self.filePath)

    def onOk(self):
        if self.ui.type.currentText() == "地震三维切片":
            SI.seismicSliceSettingWin = SeismicSliceSetting(self.filePath)
            SI.seismicSliceSettingWin.ui.show()

        if self.ui.type.currentText() == "频谱分析":
            SI.spectrumAnalysisWin = SpectrumAnalysis(self.filePath)
            SI.spectrumAnalysisWin.ui.show()

        if self.ui.type.currentText() == "变密度图":
            SI.variableDensityMapWin = VariableDensityMap(self.filePath)
            SI.variableDensityMapWin.ui.show()

    def onCancel(self):
        self.ui.close()