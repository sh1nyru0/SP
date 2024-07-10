import numpy as np
import segyio
from PyQt5.uic.properties import QtWidgets
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from qtpy import uic

from mpl_canvas import MplCanvas


class VariableDensityMap:
    def __init__(self,filename):
        self.ui = uic.loadUi('variable_density_map.ui')
        with segyio.open(filename, 'r') as segyfile:
            # 读取所有道的数据
            data = segyio.tools.collect(segyfile.trace[:])
            # 获取道数、采样点数和道间隔
            ntraces = segyfile.tracecount
            nsamples = segyfile.samples.size
            total_time = segyfile.samples[-1] / 1000  # 获取总时间（毫秒转换为秒）
            dt = total_time / nsamples  # 计算时间间隔
        # 创建时间轴和振幅轴

        t = np.arange(0, nsamples * dt, dt)
        x = np.arange(0, ntraces, 1)
        sc = MplCanvas(self, width=10, height=6, dpi=100)
        # 创建工具栏对象, 以 MplCanvas对象 和 父窗口对象作为参数
        toolbar = NavigationToolbar2QT(sc, self.ui)
        self.ui.canvasLayout.addWidget(toolbar)
        self.ui.canvasLayout.addWidget(sc)
        im = sc.axes.imshow(data.T, cmap='seismic', aspect='auto')
        sc.axes.set_xlabel('Trace Number')
        sc.axes.set_ylabel('Time(s)')
        sc.axes.set_title('Seismic Variable Density Plot')
        sc.axes.invert_yaxis()
        sc.addColorbar(im, 'Amplitude')
        sc.show()