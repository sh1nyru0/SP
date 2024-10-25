import math

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QHBoxLayout, QCheckBox, QSpacerItem, QLineEdit, QSizePolicy, \
    QWidget, QPushButton, QDialog, QFormLayout, QDialogButtonBox
from qtpy import uic

from pandas_model import PandasModel

gpslist = ['id', 'Filename', 'FH', 'UCTCT', 'Lon', 'Lat', 'Vel', 'UTCD', 'xq', 'yq', 'zq', 'gridname']
electrolist = ['id', 'Filename', 'opnum', 'freq', 'comp', 'ampa', 'emag', 'ephz', 'hmag', 'hphz', 'resistivity', 'phase', 'rho', 'phz', 'xq', 'yq', 'zq', 'gridname']
gamalist = ['id', 'Filename', 'Lon', 'Lat', 'kc', 'thc', 'uc', 'xq', 'yq', 'zq', 'gridname']
gravitylist = ['id', 'Filename', 'Line_no', 'Flight_ID', 'Lon', 'Lat', 'x', 'y', 'Height_WGS1984', 'Date', 'Time', 'ST', 'CC', 'RB', 'XACC', 'LACC', 'Still', 'Base', 'ST_real', 'Beam_vel', 'rec_grav', 'Abs_grav', 'VaccCor', 'EotvosCor', 'FaCor', 'HaccCor', 'Free_air', 'FAA_filt', 'FAA_clip', 'Level_cor', 'FAA_level', 'Fa_4600m', 'xq', 'yq', 'zq', 'gridname']
hyperlist = ['id', 'Filename', 'content', 'description', 'samples', 'lines', 'bands', 'type', 'len', 'xq', 'yq', 'zq', 'gridname']
magneticlist = ['id', 'Filename', 'Line_name', 'point', 'lon', 'lat', 'x', 'y', 'Height_WGS1984', 'Date', 'MagR', 'Magc', 'RefField', 'MagRTC', 'BCorr', 'MagBRTC', 'ACorr', 'MagF', 'MagL', 'MagML', 'MagML_Drape', 'xq', 'yq', 'zq', 'gridname']
sarlist = ['id', 'Filename', 'content', 'size', 'type', 'direction', 'proj', 'xq', 'yq', 'zq', 'gridname']
seglist = ['id', 'Filename', 'opnum', 'olnum', 'ns', 'dt', 'e', 'n', 'ampl', 'xq', 'yq', 'zq', 'gridname']
lists = ['-', gpslist, sarlist, seglist, gamalist, electrolist, magneticlist, gravitylist, hyperlist]
datanames = ['-', 'gps_data', 'sar_data', 'seg_data', 'gama_data', 'electro_data', 'magnetic_data', 'gravity_data', 'hyper_data']
titles = ['-', 'gps数据', '地基合成孔径雷达数据', '地震数据', '放射性数据', '电法数据', '磁法数据', '重力数据', '高光谱数据']

class DB:
    def __init__(self, connection=None, tableid=None, filename=None):
        self.connection = connection
        self.page = 0
        self.column_names = lists[tableid]
        self.dataname = datanames[tableid]
        self.title = titles[tableid]
        self.ui = uic.loadUi('db.ui')
        self.selectui = None
        self.cbs = []
        self.les = []
        self.init()
        self.filename = filename
        if filename:
            self.loadfile()
        self.ui.btn_delete.clicked.connect(self.delete)
        self.ui.btn_select.clicked.connect(self.select)
        self.ui.btn_add.clicked.connect(self.add)
        self.ui.btn_up.clicked.connect(self.up)
        self.ui.btn_down.clicked.connect(self.down)
        self.ui.btn_first.clicked.connect(self.first)
        self.ui.btn_end.clicked.connect(self.end)
        self.ui.btn_update.clicked.connect(self.update)
        self.ui.btn_reback.clicked.connect(self.reback)
        self.ui.grid.clicked.connect(self.grid)

    def grid(self):
        cursor = self.connection.cursor()
        sql = f'SELECT Filename, gridname, xq, yq, zq FROM {self.dataname} WHERE `Filename` = %s AND `gridname` IS NOT NULL'
        cursor.execute(sql, self.filename)
        res = cursor.fetchall()
        data = np.array([res])
        columns = ['Filename', 'gridname', 'xq', 'yq', 'zq']
        data = data.reshape(data.shape[1], len(columns))
        df = pd.DataFrame(data, columns=columns)
        df = df.apply(pd.to_numeric, errors='ignore')
        model = PandasModel(df)
        self.ui.table.setModel(model)
        self.connection.commit()

    def loadfile(self):
        columns_str = ", ".join(self.column_names)
        cursor = self.connection.cursor()
        sql = f'SELECT {columns_str} FROM {self.dataname} WHERE `Filename` = %s'
        cursor.execute(sql, self.filename)
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(data.shape[1], len(self.column_names))
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.iloc[:, 1:]
        model = PandasModel(df)
        self.ui.table.setModel(model)
        self.connection.commit()

    def init(self):
        self.ui.setWindowTitle(self.title)
        cursor = self.connection.cursor()
        sql = f'SELECT * FROM {self.dataname} LIMIT %s'
        cursor.execute(sql, (500))
        res = cursor.fetchall()
        data = np.array([res])
        data_2d = data.reshape(-1, len(self.column_names))
        df = pd.DataFrame(data_2d, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.iloc[:, 1:]
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
        sql = f'SELECT {columns_str} FROM {self.dataname} WHERE {conditions_str}'
        cursor.execute(sql, tuple(conditions.values()))
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(data.shape[1], len(self.column_names))
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.iloc[:, 1:]
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
                    sql = f'UPDATE {self.dataname} SET {column_name} = %s WHERE id = %s'
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
        try :
            self.model.removeRows(rows)
        except Exception as e:
            print(e)
        for row in rows:
            row_data = []
            index = self.model.index(row, 0)
            data = self.model.data(index)
            row_data.append(data)
            ids.append(row_data)
        cursor = self.connection.cursor()
        sql = f"DELETE FROM {self.dataname} WHERE id IN (%s)" % ','.join(['%s'] * len(ids))
        try:
            cursor.execute(sql, ids)
        except Exception as e:
            print(e)
        self.connection.commit()

    def select(self):
        self.selectui = uic.loadUi("select_db.ui")
        vlayout = QVBoxLayout()
        for i in range(8):
            if self.column_names[i] != 'id':
                hlayout = QHBoxLayout()
                cb = QCheckBox(self.column_names[i], self.selectui)
                self.cbs.append(cb)
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                le = QLineEdit(self.selectui)
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
        btn_ok = QPushButton('ok', self.selectui)
        btn_cancel = QPushButton('cancel', self.selectui)
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
                if item == 'Filename':
                    line_edit.setText(self.filename)
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
            columns_str = ", ".join(self.column_names[1:])
            placeholders = ",".join(["%s"] * len(self.column_names[1:]))
            sql = f'INSERT INTO {self.dataname}({columns_str}) VALUES ({placeholders})'
            items = []
            for item in inputs:
                items.append(item.text())
            val = tuple(items)
            cursor.execute(sql, val)
            self.connection.commit()
            self.model.addRow(items)
            QMessageBox.information(
                self.ui,
                '添加数据成功',
                '添加数据成功')
        else:
            pass

    def down(self):
        cursor = self.connection.cursor()
        sql = f'SELECT COUNT(*) FROM {self.dataname}'
        rowcount = cursor.execute(sql)
        if (rowcount / 500 > self.page):
            self.page += 1
        sql = f'SELECT * FROM {self.dataname} LIMIT %s, %s'
        cursor.execute(sql, (self.page * 500 ,500))
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(-1, len(self.column_names))
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.iloc[:, 1:]
        self.model = PandasModel(df)
        self.ui.table.setModel(self.model)
        self.connection.commit()

    def up(self):
        if self.page > 0:
            self.page -= 1
        cursor = self.connection.cursor()
        sql = f'SELECT * FROM {self.dataname} LIMIT %s, %s'
        cursor.execute(sql, (self.page, 500))
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(-1, len(self.column_names))
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.iloc[:, 1:]
        self.model = PandasModel(df)
        self.ui.table.setModel(self.model)
        self.connection.commit()

    def first(self):
        cursor = self.connection.cursor()
        sql = f'SELECT * From {self.dataname} LIMIT 0, 500'
        cursor.execute(sql)
        res = cursor.fetchall()
        data = np.array([res])
        if data.shape[1] > 500:
            data = data.reshape(500, len(self.column_names))
        else:
            data = data.reshape(data.shape[1], len(self.column_names))
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.iloc[:, 1:]
        self.model = PandasModel(df)
        self.ui.table.setModel(self.model)
        self.connection.commit()

    def end(self):
        cursor = self.connection.cursor()
        sql = f'SELECT COUNT(*) FROM {self.dataname}'
        cursor.execute(sql)
        result = cursor.fetchone()
        rowcount = result[0]
        offset = math.ceil(math.floor(rowcount / 500) * 500)
        limit = 500
        sql = f'SELECT * FROM {self.dataname} LIMIT %s, %s'
        cursor.execute(sql, (offset, limit))
        res = cursor.fetchall()
        data = np.array([res])
        data = data.reshape(data.shape[1], len(self.column_names))
        df = pd.DataFrame(data, columns=self.column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        df = df.iloc[:, 1:]
        self.model = PandasModel(df)
        self.ui.table.setModel(self.model)
        self.connection.commit()

    def reback(self):
        self.ui.table.setModel(self.model)
        self.connection.commit()