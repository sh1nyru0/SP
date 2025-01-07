import numpy as np
import pandas as pd
import segyio
from mayavi import mlab
from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import MlabSceneModel, SceneEditor, MayaviScene
from traits.api import HasTraits, Instance, on_trait_change
from traitsui.api import View, Item


class SeismicSliceModel(HasTraits):
    # 场景模型实例
    scene = Instance(MlabSceneModel, ())
    # 管线实例
    plot = Instance(PipelineBase)

    def __init__(self, path, axis, colormap):
        super(SeismicSliceModel, self).__init__()
        self.path = path
        self.axis = axis
        self.colormap = colormap

    def load_data(self):
        # 打开SEGY数据文件
        segy_data = segyio.open(self.path)

        # 获取追踪数量
        number_of_traces = segy_data.tracecount
        # 获取SEGY文件头字典
        headers = segyio.tracefield.keys

        # 创建空的DataFrame用于存储SEGY文件头数据
        segy_df = pd.DataFrame(columns=list(headers.keys()))

        # 遍历SEGY文件头字典
        for header_name, byte in headers.items():
            # 将SEGY文件头数据存储到DataFrame中
            segy_df[header_name] = segy_data.attributes(byte)[:]
            segy_df['tot_traces'] = segy_data.tracecount

        # 获取道长度
        trace_length = segy_df.loc[0, 'TRACE_SAMPLE_COUNT']

        # 获取内联和横线信息
        inline_no = segy_df['INLINE_3D']
        xline_no = segy_df['CROSSLINE_3D']

        # 计算内联和横线的相对偏移量
        segy_df['i'] = inline_no - inline_no.min()
        segy_df['j'] = xline_no - xline_no.min()

        print(segy_df)

        # 创建一个空的三维体积数组
        volume = np.zeros([segy_df['i'].max() + 1, segy_df['j'].max() + 1, trace_length])

        # 遍历所有道
        for trace_number in range(0, number_of_traces):
            # 将道数据存储到三维体积数组中
            volume[segy_df.loc[trace_number, 'i']][segy_df.loc[trace_number, 'j']][:] = segy_data.trace[trace_number][:]

        # 将超过阈值的值设为NaN
        volume[volume > 1e+8] = np.nan

        # 创建标量场
        source = mlab.pipeline.scalar_field(volume)
        source.spacing = [1, 1, -1]

        return source

    #当场景被激活，或者参数发生改变，更新图像
    """@on_trait_change(['n_meridional','n_longitudinal'])"""
    @on_trait_change('scene.activated')
    def update_plot(self):
        source = self.load_data()
        if self.plot is None:# 若plot未绘制则输出plot3d
            """
            绘图语句
            self.plot = self.scene.mlab.plot3d(x, y, z, t,
                                               tube_radius=0.025, colormap="Spectral")
            """
            for axis in self.axis:
                plane = mlab.pipeline.image_plane_widget(source,
                                                         plane_orientation='{}_axes'.format(axis),
                                                         slice_index=100, colormap=self.colormap)
                self.plot = plane
            # 显示轮廓
            mlab.outline()
            mlab.colorbar()
        else: # 如果没有数据变化，将数据更新,重新赋值
            """
            self.plot.mlab_source.set(
                x=x, y=y, z=z, scalars=t
            )
            """

    # 建立视图布局
    view = View(
        Item("scene", editor=SceneEditor(scene_class=MayaviScene),
             height=250, width=300, show_label=False),
        resizable=True
    )
