import os
import pickle

import numpy as np
from qtpy import uic
from scipy.interpolate import griddata

datanames = ['-', 'gps_data', 'sar_data', 'seg_data', 'gama_data', 'electro_data', 'magnetic_data', 'gravity_data', 'hyper_data']
cdatanames = ['-', 'gps数据', '地基合成孔径雷达数据', '地震数据', '放射性数据', '电法数据', '磁法数据', '重力数据', '高光谱数据']
map = {
    'gps数据': 'gps_data',
    '地基合成孔径雷达数据': 'sar_data',
    '地震数据': 'seg_data',
    '放射性数据': 'gama_data',
    '电法数据': 'electro_data',
    '磁法数据': 'magnetic_data',
    '重力数据': 'gravity_data',
    '高光谱数据': 'hyper_data'
}

class GridWin:
    def __init__(self, connection, model, path):
        self.connection = connection
        self.ui = uic.loadUi("grid.ui")
        self.ui.setWindowTitle("网格化")
        self.df = model._data
        self.path = path
        self.ui.cbx.addItems(self.df.columns)
        self.ui.cby.addItems(self.df.columns)
        self.ui.cbz.addItems(self.df.columns)
        self.ui.buttonBox.accepted.connect(self.ok)
        self.ui.buttonBox.rejected.connect(self.cancel)

    def ok(self):
        spacingx  = float(self.ui.spacingx.text())
        spacingy  = float(self.ui.spacingy.text())
        xname = self.ui.cbx.currentText()
        yname = self.ui.cby.currentText()
        zname = self.ui.cbz.currentText()
        self.x = self.df[xname]
        self.y = self.df[yname]
        self.z = self.df[zname]
        self.x = [float(item) for item in self.x]
        self.y = [float(item) for item in self.y]
        self.z = [float(item) for item in self.z]
        x1 = np.arange(min(self.x), max(self.x), spacingx)
        y1 = np.arange(min(self.y), max(self.y), spacingy)
        xq, yq = np.meshgrid(x1, y1)
        zq = griddata((self.x, self.y), self.z, (xq, yq), method=self.ui.cbmethod.currentText())
        xq = pickle.dumps(xq)
        yq = pickle.dumps(yq)
        zq = pickle.dumps(zq)
        # 反序列化 xq = pickle.loads(xq)
        parent_dir, current_dir = os.path.split(self.path)
        grandparent_dir, db_dir = os.path.split(parent_dir)
        filename = current_dir + "_grid"
        gridname = self.ui.name.text()
        cursor = self.connection.cursor()
        sql = f'INSERT INTO {map[db_dir]}(Filename, xq, yq, zq, gridname) VALUES (%s, %s, %s, %s, %s)'
        val = (filename, xq, yq, zq, gridname)
        cursor.execute(sql, val)
        self.connection.commit()
        self.ui.close()

    def cancel(self):
        self.ui.close()