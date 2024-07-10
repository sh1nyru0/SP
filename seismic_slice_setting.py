from qtpy import uic

from seismicSliceModel import SeismicSliceModel


class SeismicSliceSetting:
    def __init__(self,filePath):
        self.ui = uic.loadUi('seismic_slice_setting.ui')
        self.ui.buttonBox.accepted.connect(self.onOk)
        self.ui.buttonBox.rejected.connect(self.onCancel)
        self.filePath = filePath

    def onOk(self):
        direction = []
        if self.ui.btn_x.isChecked():
            direction.append('x')
        if self.ui.btn_y.isChecked():
            direction.append('y')
        if self.ui.btn_z.isChecked():
            direction.append('z')
        if self.filePath is not None:
            model = SeismicSliceModel(self.filePath, direction, self.ui.comboBox.currentText())
            model.configure_traits()

    def onCancel(self):
        self.ui.close()