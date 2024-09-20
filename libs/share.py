from PyQt5.QtCore import QObject, pyqtSignal, QModelIndex
from pandas_model import PandasModel

class SI:
    mainWin = None
    startWin = None
    newProjectWin = None
    session = None
    filterWin = None
    importdbWin = None
    seismicSettingWin = None
    seismicSliceSettingWin = None
    spectrumAnalysisWin = None
    variableDensityMapWin = None
    graMagSettingWin = None
    sactionalViewWin = None
    sactionalViewMpl = None
    chooseDataTableWin = None
    gridWin = None

    # 保存MDI的子窗口对象
    subWinTable = {}
    currentProject = ""


# 自定义信号源对象类型，一定要继承自QObject
class MySignals(QObject):
    loadData = pyqtSignal(PandasModel)
    projectFile = pyqtSignal(str,str)
    project = pyqtSignal()
    log = pyqtSignal(str)
    dataPath = pyqtSignal(str)
    msgBox = pyqtSignal(str, str)
