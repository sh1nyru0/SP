import pickle

from qtpy import uic

from basemap_view_mpl import BasemapViewMpl
from libs.share import SI


class BaseMapView:

    def __init__(self):
        self.ui = uic.loadUi('basemap_view.ui')
        self.ui.buttonBox.accepted.connect(self.onOk)
        self.ui.buttonBox.accepted.connect(self.onCancel)
        with open('select_data.pkl', 'rb') as f:
            self.df = pickle.load(f)
        for column in self.df.columns:
            self.ui.cb1.addItem(column)
            self.ui.cb2.addItem(column)
            self.ui.cb3.addItem(column)

    def onCancel(self):
        self.ui.close()

    def onOk(self):
        SI.baseMapViewMpl = BasemapViewMpl(self.df, self.ui.cb1.currentText(), self.ui.cb2.currentText(), self.ui.cb3.currentText())
        SI.baseMapViewMpl.ui.show()