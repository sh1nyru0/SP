import numpy as np
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

gpslist = ['id', 'Filename', 'FH', 'UCTCT', 'Lon', 'Lat', 'Vel', 'UTCD', 'xq', 'yq', 'zq', 'gridname']
electrolist = ['id', 'Filename', 'opnum', 'freq', 'comp', 'ampa', 'emag', 'ephz', 'hmag', 'hphz', 'resistivity',
               'phase', 'rho', 'phz', 'xq', 'yq', 'zq', 'gridname']
gamalist = ['id', 'Filename', 'Lon', 'Lat', 'kc', 'thc', 'uc', 'xq', 'yq', 'zq', 'gridname']
gravitylist = ['id', 'Filename', 'Line_no', 'Flight_ID', 'Lon', 'Lat', 'x', 'y', 'Height_WGS1984', 'Date', 'Time', 'ST',
               'CC', 'RB', 'XACC', 'LACC', 'Still', 'Base', 'ST_real', 'Beam_vel', 'rec_grav', 'Abs_grav', 'VaccCor',
               'EotvosCor', 'FaCor', 'HaccCor', 'Free_air', 'FAA_filt', 'FAA_clip', 'Level_cor', 'FAA_level',
               'Fa_4600m', 'xq', 'yq', 'zq', 'gridname']
hyperlist = ['id', 'Filename', 'content', 'description', 'samples', 'lines', 'bands', 'type', 'len', 'xq', 'yq', 'zq',
             'gridname']
magneticlist = ['id', 'Filename', 'Line_name', 'point', 'lon', 'lat', 'x', 'y', 'Height_WGS1984', 'Date', 'MagR',
                'Magc', 'RefField', 'MagRTC', 'BCorr', 'MagBRTC', 'ACorr', 'MagF', 'MagL', 'MagML', 'MagML_Drape', 'xq',
                'yq', 'zq', 'gridname']
sarlist = ['id', 'Filename', 'content', 'size', 'type', 'direction', 'proj', 'xq', 'yq', 'zq', 'gridname']
seglist = ['id', 'Filename', 'opnum', 'olnum', 'ns', 'dt', 'e', 'n', 'ampl', 'xq', 'yq', 'zq', 'gridname']
lists = ['-', gpslist, sarlist, seglist, gamalist, electrolist, magneticlist, gravitylist, hyperlist]
datanames = ['-', 'gps_data', 'sar_data', 'seg_data', 'gama_data', 'electro_data', 'magnetic_data', 'gravity_data',
             'hyper_data']
titles = ['-', 'gps数据', '地基合成孔径雷达数据', '地震数据', '放射性数据', '电法数据', '磁法数据', '重力数据',
          '高光谱数据']


class PandasModel(QAbstractTableModel):
    def __init__(self, connection, tableid=None, df=None, filename=None, page_size=500, parent=None):
        super().__init__(parent)
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.page_size = page_size  # 每页数据量
        self.current_page = 0  # 当前页号
        self.column_names = lists[tableid]
        self.dataname = datanames[tableid]
        self.title = titles[tableid]
        self._original_data = {}  # 使用字典来保存原始数据
        self._dirty_cells = set()  # 用集合来记录被修改的单元格索引
        if df is not None:
            self._data = df
        else:
            self._data = self._load_data()  # 加载第一页数据

        if filename:
            self.filename = filename

    def is_dirty(self):
        return bool(self._dirty_cells)

    def get_dirty_cells(self):
        return self._dirty_cells

    def get_value(self, row, column):
        if 0 <= row < self.rowCount() and 0 <= column < self.columnCount():
            return self._data.iloc[row, column]
        return None

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable  # 默认情况下，返回可编辑标志

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < self.rowCount() and 0 <= index.column() < self.columnCount():
            if value:
                row = index.row()
                col = index.column()
                original_value = self._data.iloc[row, col]
                if (row, col) not in self._original_data:  # 保存原始值
                    self._original_data[(row, col)] = original_value
                if str(original_value) != str(value):
                    self._dirty_cells.add((row, col))
                self._data.iloc[row, col] = value
                self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
                return True
        return False

    def _load_data(self):
        """从数据库加载当前页的数据"""
        columns_str = ", ".join(self.column_names)
        offset = self.current_page * self.page_size
        sql = f"SELECT {columns_str} FROM {self.dataname} LIMIT {self.page_size} OFFSET {offset}"
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        data = np.array([res])
        data_2d = data.reshape(-1, len(self.column_names))
        df = pd.DataFrame(data_2d, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.iloc[:, 1:]
        return df

    def rowCount(self, parent=None):
        """返回当前页的行数"""
        return self._data.shape[0]

    def columnCount(self, parent=None):
        """返回列数"""
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        """按需返回单元格数据"""
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        value = self._data.iloc[index.row(), index.column()]
        return str(value)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """显示列名或行号"""
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._data.columns[section])
        else:
            return str(section + 1 + self.current_page * self.page_size)

    def nextPage(self):
        """跳转到下一页"""
        self.current_page += 1
        self._data = self._load_data()
        self.layoutChanged.emit()  # 通知视图数据已更新

    def prevPage(self):
        """跳转到上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self._data = self._load_data()
            self.layoutChanged.emit()

    def firstPage(self):
        """跳转到首页"""
        self.current_page = 0
        self._data = self._load_data()
        self.layoutChanged.emit()

    def lastPage(self):
        """跳转到末页"""
        sql = f"select * from {self.dataname}"
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        all_data_rows = len(np.array(res))
        self.current_page = int(all_data_rows / 500)
        self._data = self._load_data()
        self.layoutChanged.emit()
