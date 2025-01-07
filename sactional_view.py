import pickle

import numpy as np
import pandas as pd
from qtpy import uic

from libs.share import SI
from sactional_view_mpl import SactionalViewMpl


class SactionalView:
    # def __init__(self,filePath):
    #     self.ui = uic.loadUi('sactional_view.ui')
    #     self.ui.buttonBox.accepted.connect(self.onOk)
    #     self.ui.buttonBox.rejected.connect(self.onCancel)
    #     self.filePath = filePath
    #     self.df = self.read_csv(self.filePath)
    #     for column in self.df.columns:
    #         self.ui.cb1.addItem(column)
    #         self.ui.cb2.addItem(column)

    def __init__(self):
        self.ui = uic.loadUi('sactional_view.ui')
        self.ui.buttonBox.accepted.connect(self.onOk)
        self.ui.buttonBox.rejected.connect(self.onCancel)
        with open('select_data.pkl', 'rb') as f:
            self.df = pickle.load(f)
        for column in self.df.columns:
            self.ui.cb1.addItem(column)
            self.ui.cb2.addItem(column)

    def onOk(self):
        SI.sactionalViewMpl = SactionalViewMpl(self.df, self.ui.cb1.currentText(), self.ui.cb2.currentText())
        SI.sactionalViewMpl.ui.show()

    def onCancel(self):
        self.ui.close()

    def read_csv(self, file_path, skip_rows=0, selected_columns=None):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        column_names = lines[0].rstrip('\n').split(',')
        data = [line.rstrip('\n').split(',') for line in lines[1 + skip_rows:]]
        # 填充缺失的数据为 NaN
        for row in data:
            if len(row) < len(column_names):
                row += [np.nan] * (len(column_names) - len(row))
                # 创建 DataFrame，并将数据转换为数值类型
        df = pd.DataFrame(data, columns=column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        if selected_columns:
            df = df[selected_columns]
        return df