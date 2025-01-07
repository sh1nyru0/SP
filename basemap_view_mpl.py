import numpy as np
from matplotlib.colors import BoundaryNorm
from mpl_toolkits.basemap import Basemap
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from qtpy import uic
class BasemapViewMpl:
    def __init__(self, df, xname, yname, zname):
        self.ui = uic.loadUi('basemap_view_mpl.ui')

        gravity_data = df[[xname, yname, zname]]
        gravity_data.columns = ['longitude', 'latitude', 'bouguer_anomaly']

        gravity_data = gravity_data.dropna(subset=['bouguer_anomaly'])
        self.gravity_points = [(float(row['latitude']), float(row['longitude']), float(row['bouguer_anomaly'])) for _, row in gravity_data.iterrows()]

        # 添加 Matplotlib 图形
        self.figure = Figure(figsize=(11, 9), dpi=80)
        self.canvas = FigureCanvas(self.figure)
        self.ui.canvasLayout.addWidget(self.canvas)

        # 初始化图形
        self.ax = self.figure.add_subplot(111)
        self.m = Basemap(projection='spstere', boundinglat=-60, lon_0=0, resolution='l', ax=self.ax)
        self.m.drawcoastlines()
        self.m.drawcountries()
        self.m.drawparallels(np.arange(-90., 0., 10.), labels=[1, 0, 0, 0])
        self.m.drawmeridians(np.arange(-180., 180., 10.), labels=[0, 0, 0, 1])
        self.m.etopo()
        self.vmin_magnetic = -120
        self.vmax_magnetic = 120
        self.plot_initial_layers()
        # 显示颜色条
        self.cbar_gravity = self.figure.colorbar(self.gravity_layer, ax=self.ax, orientation='horizontal',
                                                 fraction=0.03, pad=0.05, aspect=40)
        self.cbar_gravity.set_label("重力值", fontsize=10, labelpad=-10)  # 标签放置在左侧
        self.cbar_gravity.ax.tick_params(labelsize=8)

        # 调整整体布局
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

        # 更新画布以显示图形
        self.canvas.draw()

    def plot_heatmap_layer_with_clipping(self, m, points, cmap, label, vmin, vmax):
        latitudes = [point[0] for point in points]
        longitudes = [point[1] for point in points]
        values = [point[2] for point in points]

        x, y = m(longitudes, latitudes)
        norm = BoundaryNorm(boundaries=np.linspace(vmin, vmax, 100), ncolors=256)

        sc = m.scatter(x, y, c=values, cmap=cmap, norm=norm, label=label, s=10, alpha=0.8, edgecolors="k", linewidth=0)
        return sc

    def plot_initial_layers(self):
        self.gravity_layer = self.plot_heatmap_layer_with_clipping(self.m, self.gravity_points, cmap='coolwarm',
                                                              label="重力", vmin=-200, vmax=200)

