from matplotlib.backends.backend_qt import NavigationToolbar2QT
from qtpy import uic

from mpl_canvas import MplCanvas


class SactionalViewMpl:
    def __init__(self, df, xname, yname):
        self.ui = uic.loadUi('sactional_view_mpl.ui')
        x = df[xname]
        y = df[yname]
        sc = MplCanvas(self, width=10, height=6, dpi=100)
        # 创建工具栏对象, 以 MplCanvas对象 和 父窗口对象作为参数
        toolbar = NavigationToolbar2QT(sc, self.ui)
        self.ui.canvasLayout.addWidget(toolbar)
        self.ui.canvasLayout.addWidget(sc)
        sc.axes.plot(x, y, marker='o', linestyle='-')
        sc.axes.set_xlabel('侧线位置')
        sc.axes.set_ylabel('磁异常值')
        sc.axes.set_title('磁异常剖面')
        sc.axes.grid(True)
        sc.show()
