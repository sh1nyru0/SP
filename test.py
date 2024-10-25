import sqlite3
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWidgets import QApplication, QTableView, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout

class LazyDatabaseModel(QAbstractTableModel):
    def __init__(self, db_path, page_size=100, parent=None):
        super().__init__(parent)
        self.db_path = db_path  # 数据库路径
        self.page_size = page_size  # 每页数据量
        self.current_page = 0  # 当前页号
        self._data = self._load_data()  # 加载第一页数据

    def _load_data(self):
        """从数据库加载当前页的数据"""
        offset = self.current_page * self.page_size
        query = f"SELECT * FROM data LIMIT {self.page_size} OFFSET {offset}"

        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
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
        with sqlite3.connect(self.db_path) as conn:
            total_rows = conn.execute("SELECT COUNT(*) FROM data").fetchone()[0]
        self.current_page = (total_rows - 1) // self.page_size
        self._data = self._load_data()
        self.layoutChanged.emit()

# 分页查看器类
class DataFrameViewer(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.model = LazyDatabaseModel(db_path, page_size=100)

        # 创建 QTableView 和分页按钮
        self.view = QTableView()
        self.view.setModel(self.model)

        self.first_button = QPushButton("首页")
        self.prev_button = QPushButton("上一页")
        self.next_button = QPushButton("下一页")
        self.last_button = QPushButton("末页")
        self.page_label = QLabel(f"当前页: 1")

        # 绑定按钮事件
        self.first_button.clicked.connect(self.first_page)
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        self.last_button.clicked.connect(self.last_page)

        # 布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.first_button)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.page_label)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.last_button)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def next_page(self):
        """跳转到下一页并更新页码显示"""
        self.model.nextPage()
        self.update_page_label()

    def prev_page(self):
        """跳转到上一页并更新页码显示"""
        self.model.prevPage()
        self.update_page_label()

    def first_page(self):
        """跳转到首页并更新页码显示"""
        self.model.firstPage()
        self.update_page_label()

    def last_page(self):
        """跳转到末页并更新页码显示"""
        self.model.lastPage()
        self.update_page_label()

    def update_page_label(self):
        """更新页码显示"""
        self.page_label.setText(f"当前页: {self.model.current_page + 1}")

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # 使用 example.db 数据库
    db_path = "example.db"

    viewer = DataFrameViewer(db_path)
    viewer.resize(800, 600)
    viewer.show()

    sys.exit(app.exec_())
