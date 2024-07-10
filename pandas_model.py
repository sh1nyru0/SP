from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex

class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data
        self._original_data = {}  # 使用字典来保存原始数据
        self._dirty_cells = set()  # 用集合来记录被修改的单元格索引

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
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
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            else:
                return str(self._data.index[section])
        return None

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