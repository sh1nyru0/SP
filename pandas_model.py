import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

class PandasModel(QAbstractTableModel):
    def __init__(self, data, page_size=500):
        QAbstractTableModel.__init__(self)
        self._data = data
        self.page_size = page_size  # 每页的行数
        self.current_page = 0  # 当前页号
        self._data_cache = {}  # 使用缓存减少磁盘访问
        self._original_data = {}  # 使用字典来保存原始数据
        self._dirty_cells = set()  # 用集合来记录被修改的单元格索引

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row, col = index.row(), index.column()
        # 返回单元格的显示文本
        if role == Qt.DisplayRole or role == Qt.EditRole:  # 增加对 Qt.EditRole 的处理
            return str(self._data.iloc[row, col])
        return None

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

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """显示列名和行号"""
        # if role == Qt.DisplayRole:
        #     if orientation == Qt.Horizontal:
        #         return self._data.columns[section]
        #     else:
        #         return str(self._data.index[section])
        # return None
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._data.columns[section])
        else:
            return str(section + 1 + self.current_page * self.page_size)

    def removeRow(self, row, parent=QModelIndex()):
        self.beginRemoveRows(parent or Qt.QModelIndex(), row, row)
        self._data = self._data.drop(self._data.index[row]).reset_index(drop=True)
        self.endRemoveRows()
        return True

    def removeRows(self, rows, parent=QModelIndex()):
        self.beginRemoveRows(parent, min(rows), max(rows))
        self._data.drop(self._data.index[rows], inplace=True)
        self._data.reset_index(drop=True, inplace=True)
        self.endRemoveRows()
        return True

    # 添加一行数据的函数
    def addRow(self, new_row_data):
        row_count = self.rowCount()
        self.beginInsertRows(QModelIndex(), row_count, row_count)

        # 将新行数据添加到 DataFrame 中
        new_row_df = pd.DataFrame([new_row_data], columns=self._data.columns)
        self._data = pd.concat([self._data, new_row_df], ignore_index=True)

        self.endInsertRows()

    def is_dirty(self):
        return bool(self._dirty_cells)

    def get_dirty_cells(self):
        return self._dirty_cells

    def undo_cell_changes(self, index):
        if index.isValid():
            row = index.row()
            col = index.column()
            if (row, col) in self._original_data:  # 检查原始数据是否存在
                original_value = self._original_data[(row, col)]
                self._data.iloc[row, col] = original_value
                self._original_data[(row, col)] = self._data.iloc[row, col]  # 更新原始数据记录
                self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
                return True
        return False

    def flags(self, index):
        if index.column() == 0:  # 第一列不可编辑
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled  # 只返回可选和可启用标志
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable  # 默认情况下，返回可编辑标志

    def get_value(self, row, column):
        if 0 <= row < self.rowCount() and 0 <= column < self.columnCount():
            return self._data.iloc[row, column]
        return None

    def nextPage(self):
        """跳转到下一页"""
        if (self.current_page + 1) * self.page_size < len(self._data):
            self.current_page += 1
            self.layoutChanged.emit()  # 通知视图数据已更新

    def prevPage(self):
        """跳转到上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.layoutChanged.emit()

    def firstPage(self):
        """跳转到首页"""
        if self.current_page != 0:
            self.current_page = 0
            self.layoutChanged.emit()

    def lastPage(self):
        """跳转到末页"""
        last_page = (len(self._data) - 1) // self.page_size
        if self.current_page != last_page:
            self.current_page = last_page
            self.layoutChanged.emit()