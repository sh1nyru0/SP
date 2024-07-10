import numpy as np
import segyio
import pyqtgraph as pg
from qtpy import uic


class SpectrumAnalysis:
    def __init__(self, filename):
        self.pw = pg.GraphicsLayoutWidget()
        self.ui = uic.loadUi('spectrum_analysis.ui')
        self.filename = filename
        with segyio.open(filename, 'r') as segyfile:
            tracecount = segyfile.tracecount
        self.ui.sliderbar.setMinimum(1)
        self.ui.sliderbar.setMaximum(tracecount)
        self.ui.sliderbar.valueChanged.connect(self.update_label)
        self.ui.canvasLayout.addWidget(self.pw)
        self.updatePlot()
        self.ui.sliderbar.valueChanged.connect(self.updatePlot)

    def update_label(self, value):
        self.ui.label_num.setText(f'序号:{value}')

    def updatePlot(self):
        with segyio.open(self.filename, 'r') as segyfile:
            tracenum = self.ui.sliderbar.value()
            trace_data = segyfile.trace[tracenum]
            fft_data = np.fft.fft(trace_data)
            phase_spectrum = np.angle(fft_data)
            amplitude_spectrum = np.abs(fft_data)
        self.pw.clear()
        self.pw.setBackground('w')
        plot1 = self.pw.addPlot()# 相位图
        plot1.setTitle('Phase Spectrum')
        plot1.setLabel('bottom', "Frequency", units='Hz')
        plot1.setLabel('left', "Phase")
        ps = pg.PlotCurveItem(phase_spectrum, pen='b')
        plot1.addItem(ps)

        plot2 = self.pw.addPlot()# 振幅图
        plot2.setTitle('Amplitude Spectrum')
        plot2.setLabel('bottom', "Frequency", units='Hz')
        plot2.setLabel('left', "Amplitude")
        ams = pg.PlotCurveItem(amplitude_spectrum, pen='b')
        plot2.addItem(ams)

        plot3 = self.pw.addPlot()# 波形图
        plot3.setTitle('Waveform')
        plot3.setLabel('bottom', "Time", units='s')
        plot3.setLabel('left', 'Amplitude')
        wave = pg.PlotCurveItem(trace_data, pen='b')
        plot3.addItem(wave)