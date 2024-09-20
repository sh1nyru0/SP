from qtpy import uic

import GridDB
from data_base import DataBase
from electro_db import ElectroDB
from gama_db import GamaDB
from gps_db import GpsDB
from gravity_db import GravityDB
from hyper_db import HyperDB
from libs.share import SI
from magnetic_db import MagneticDB
from sar_db import SarDB
from seg_db import SegDB


class ChooseDataTable:
    def __init__(self):
        self.ui = uic.loadUi("choose_data_table.ui")
        self.ui.buttonBox.accepted.connect(self.btn_ok)

    def btn_ok(self):
        id = self.ui.buttonGroup.checkedId()
        # id从上到下依次为-2 -3 -4 -5 -6 -7 -8 -9 -10
        SI.mainWin._openSubWin(DataBase)
        SI.subWinTable[str(DataBase)]['subWin'].setWindowTitle("数据库")
        if id == -2:# 重力
            SI.mainWin._openSubWin(GravityDB)
            SI.subWinTable[str(DataBase)]['subWin'].setWindowTitle("重力数据表")
        if id == -3:# 磁法
            SI.mainWin._openSubWin(MagneticDB)
            SI.subWinTable[str(DataBase)]['subWin'].setWindowTitle("磁法数据表")
        if id == -4:# 电法
            SI.mainWin._openSubWin(ElectroDB)
            SI.subWinTable[str(DataBase)]['subWin'].setWindowTitle("电法数据表")
        if id == -5:# 地震
            SI.mainWin._openSubWin(SegDB)
            SI.subWinTable[str(DataBase)]['subWin'].setWindowTitle("地震数据表")
        if id == -6:# gps
            SI.mainWin._openSubWin(GpsDB)
            SI.subWinTable[str(DataBase)]['subWin'].setWindowTitle("gps数据表")
        if id == -7:# 放射性
            SI.mainWin._openSubWin(GamaDB)
            SI.subWinTable[str(DataBase)]['subWin'].setWindowTitle("放射性数据表")
        if id == -8:# 高光谱
            SI.mainWin._openSubWin(HyperDB)
            SI.subWinTable[str(DataBase)]['subWin'].setWindowTitle("高光谱数据表")
        if id == -9:# 地基合成孔径雷达
            SI.mainWin._openSubWin(SarDB)
            SI.subWinTable[str(DataBase)]['subWin'].setWindowTitle("地基合成孔径雷达数据表")
        if id == -10:# 网格化
            SI.mainWin._openSubWin(GridDB)
            SI.subWinTable[str(DataBase)]['subWin'].setWindowTtile("网格化数据表")