import pandas as pd
from PyQt5.QtCore import QObject, pyqtSignal
from pandas_model import PandasModel

share_data = None

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
    baseMapViewWin = None
    sactionalViewMpl = None
    baseMapViewMpl = None
    chooseDataTableWin = None
    gridWin = None
    editPluginWin = None
    pluginManagerWin = None

    # 保存MDI的子窗口对象
    subWinTable = {}
    currentProject = ""


# 自定义信号源对象类型，一定要继承自QObject
class MySignals(QObject):
    loadData = pyqtSignal(PandasModel)
    projectFile = pyqtSignal(str, str)  # projectpath projectname
    project = pyqtSignal()
    log = pyqtSignal(str)
    dataPath = pyqtSignal(str)
    msgBox = pyqtSignal(str, str)
    filterdf = pyqtSignal(pd.DataFrame, str, str)  # df dataname filename
