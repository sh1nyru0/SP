import csv
import os
import shutil

from PyQt5.QtWidgets import QMessageBox
from scipy.interpolate import griddata
import numpy as np
import pandas as pd
from qtpy import uic
class Grid:
    def __init__(self,path):
        self.ui = uic.loadUi("grid.ui")
        self.df = pd.read_csv(path)
        self.path = path
        columns = self.df.columns
        for columm in columns:
            self.ui.cbx.addItem(columm)
            self.ui.cby.addItem(columm)
            self.ui.cbz.addItem(columm)
        self.ui.buttonBox.accepted.connect(self.btn_ok)

    def btn_ok(self):
        x = self.df[self.ui.cbx.currentText()]
        y = self.df[self.ui.cby.currentText()]
        z = self.df[self.ui.cbz.currentText()]
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)
        xq, yq = np.meshgrid(x, y)
        zq = griddata((x, y), z, (xq, yq), method='nearest')
        row,col = xq.shape[0], xq.shape[1]
        nx = list()
        ny = list()
        nz = list()
        path = os.path.basename(self.path)
        path = os.path.splitext(path)[0]
        for i in range(row):
            for j in range(col):
                nx.append(xq[i][j])
                ny.append(yq[i][j])
                nz.append(zq[i][j])
        data = list(zip(nx,ny,nz))
        column_names = [self.ui.cbx.currentText(), self.ui.cby.currentText(), self.ui.cbz.currentText()]
        df = pd.DataFrame(data, columns=column_names)
        df.insert(loc=0, column='Filename', value=path + '_grid')
        df.to_csv(os.path.dirname(self.path) + '/' + path + '_grid' + '.csv', encoding='utf-8', index=False)
