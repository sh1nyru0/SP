from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

# 创建一个继承自FigureCanvasQTAgg的类
# 也就是一个 QWidget 的子类
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        # 一定要把Figure对象作为参数传递进去
        super().__init__(fig)

    def addColorbar(self, im, label):
        self.cbar = self.figure.colorbar(im, ax=self.axes)
        self.cbar.set_label(label)
