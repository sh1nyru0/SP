import math

import numpy as np
import pandas as pd
import pymysql
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QHBoxLayout, QCheckBox, QSpacerItem, QLineEdit, QSizePolicy, \
    QWidget, QPushButton, QDialog, QFormLayout, QDialogButtonBox
from qtpy import uic

from pandas_model import PandasModel


class GamaDB:
    def __init__(self):
        self.connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='123456',
            db='geo',
            charset='utf8'
        )
        self.page = 0
        self.column_names = ['id', 'Filename', 'Lon', 'Lat', 'kc', 'thc', 'uc']
        self.ui = uic.loadUi('db.ui')
        self.selectui = None
        self.cbs = []
        self.les = []
        self.init()
        self.ui.btn_delete.clicked.connect(self.delete)
        self.ui.btn_select.clicked.connect(self.select)
        self.ui.btn_add.clicked.connect(self.add)
        self.ui.btn_up.clicked.connect(self.up)
        self.ui.btn_down.clicked.connect(self.down)
        self.ui.btn_first.clicked.connect(self.first)
        self.ui.btn_end.clicked.connect(self.end)
        self.ui.btn_update.clicked.connect(self.update)
        self.ui.btn_reback.clicked.connect(self.reback)

    def __del__(self):
        self.connection.close()

    def init(self):
        cursor = self.connection.cursor()
        sql = 'SELECT * FROM gama_data LIMIT %s'
        cursor.execute(sql, (500))
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(500, 7)
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        self.model = PandasModel(df)
        self.ui.table.setModel(self.model)
        self.connection.commit()

    def on_ok_clicked(self):
        columns_str = ", ".join(self.column_names)
        conditions = {}
        for i in range(len(self.cbs)):
            if self.cbs[i].isChecked():
                conditions[self.cbs[i].text()] = self.les[i].text()
        conditions_str = "AND ".join([f"{key} = %s" for key in conditions.keys()])
        cursor = self.connection.cursor()
        sql = f'SELECT {columns_str} FROM gama_data WHERE {conditions_str}'
        cursor.execute(sql, tuple(conditions.values()))
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(data.shape[1], 7)
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        model = PandasModel(df)
        self.ui.table.setModel(model)
        self.connection.commit()
        self.selectui.close()

    def on_cancel_clicked(self):
        self.selectui.close()

    def update(self):
        if self.model.is_dirty():
            dirty_cells = self.model.get_dirty_cells()
            for row, col in dirty_cells:
                choice = QMessageBox.question(
                    self.ui,
                    '确认',
                    f'单元格({row}, {col})被修改，需要保存修改吗？'
                )
                index = self.model.index(row, col)
                if choice == QMessageBox.No:
                    self.model.undo_cell_changes(index)
                else:
                    cursor = self.connection.cursor()
                    id = self.model.get_value(row, 0)
                    value = self.model.get_value(row, col)
                    column_name = self.column_names[col]
                    sql = f'UPDATE gama_data SET {column_name} = %s WHERE id = %s'
                    cursor.execute(sql, (value, id))
                    self.connection.commit()
        else:
            QMessageBox.warning(
                self.ui,
                '无修改',
                '没有修改的内容'
            )
        self.model._dirty_cells = set()

    def delete(self):
        indexes = self.ui.table.selectionModel().selectedRows()
        rows = sorted([index.row() for index in indexes], reverse=True)
        ids = []
        self.model.removeRows(rows)
        for row in rows:
            row_data = []
            index = self.model.index(row, 0)
            data = self.model.data(index)
            row_data.append(data)
            ids.append(row_data)
        cursor = self.connection.cursor()
        sql = "DELETE FROM gama_data WHERE id IN (%s)" % ','.join(['%s'] * len(ids))
        cursor.execute(sql, ids)
        self.connection.commit()

    def select(self):
        self.selectui = uic.loadUi("select_db.ui")
        vlayout = QVBoxLayout()
        for i in range(7):
            if self.column_names[i] != 'id':
                hlayout = QHBoxLayout()
                cb = QCheckBox(self.column_names[i])
                self.cbs.append(cb)
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                le = QLineEdit()
                self.les.append(le)
                hlayout.addWidget(cb)
                hlayout.addItem(spacer)
                hlayout.addWidget(le)
                hlayout.setStretch(3, 10)
                hlayout.setStretch(1, 10)
                hlayout.setStretch(6, 10)
                vlayout.addLayout(hlayout)

        container = QWidget()
        container.setLayout(vlayout)
        btn_ok = QPushButton('ok')
        btn_cancel = QPushButton('cancel')
        self.selectui.layout().addWidget(container)
        btn_ok.clicked.connect(self.on_ok_clicked)
        btn_cancel.clicked.connect(self.on_cancel_clicked)
        hlayout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(spacer)
        hlayout.addWidget(btn_ok)
        hlayout.addWidget(btn_cancel)
        hlayout.setStretch(0, 8)
        hlayout.setStretch(1, 8)
        hlayout.setStretch(2, 8)
        vlayout.addLayout(hlayout)
        self.selectui.show()

    def add(self):
        dialog = QDialog()
        dialog.setWindowTitle("添加数据")

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        inputs = []
        for item in self.column_names:
            if item != 'id':
                line_edit = QLineEdit(dialog)
                inputs.append(line_edit)
                form_layout.addRow(item, line_edit)

        layout.addLayout(form_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)
        if dialog.exec_() == QDialog.Accepted:
            cursor = self.connection.cursor()
            sql = 'INSERT INTO gama_data(Filename, Lon, Lat, kc, thc, uc) VALUES (%s, %s, %s, %s, %s, %s)'
            items = []
            for item in inputs:
                items.append(item.text())
            val = tuple(items)
            cursor.execute(sql, val)
            self.connection.commit()
            QMessageBox.information(
                self.ui,
                '添加数据成功',
                '添加数据成功')
        else:
            pass

    def down(self):
        cursor = self.connection.cursor()
        sql = 'SELECT COUNT(*) FROM gama_data'
        rowcount = cursor.execute(sql)
        if (rowcount / 500 > self.page):
            self.page += 1
        sql = 'SELECT * FROM gama_data LIMIT %s, %s'
        cursor.execute(sql, (self.page * 500 ,500))
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(500, 7)
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        self.model = PandasModel(df)
        self.ui.table.setModel(self.model)
        self.connection.commit()

    def up(self):
        if self.page > 0:
            self.page -= 1
        cursor = self.connection.cursor()
        sql = 'SELECT * FROM gama_data LIMIT %s, %s'
        cursor.execute(sql, (self.page, 500))
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(500, 7)
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        self.model = PandasModel(df)
        self.ui.table.setModel(self.model)
        self.connection.commit()

    def first(self):
        cursor = self.connection.cursor()
        sql = 'SELECT * From gama_data LIMIT 0, 500'
        cursor.execute(sql)
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(500, 7)
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        self.model = PandasModel(df)
        self.ui.table.setModel(self.model)
        self.connection.commit()

    def end(self):
        cursor = self.connection.cursor()
        sql = 'SELECT COUNT(*) FROM gravity_data'
        cursor.execute(sql)
        result = cursor.fetchone()
        rowcount = result[0]
        offset = math.ceil(math.floor(rowcount / 500) * 500)
        limit = 500
        sql = 'SELECT * FROM gama_data LIMIT %s, %s'
        cursor.execute(sql, (offset, limit))
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(data.shape[1], 7)
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        self.model = PandasModel(df)
        self.ui.table.setModel(self.model)
        self.connection.commit()

    def reback(self):
        self.ui.table.setModel(self.model)
        self.connection.commit()