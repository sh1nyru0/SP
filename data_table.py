import pymysql
from PyQt5.QtCore import QDataStream, QIODevice, QByteArray, Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QAbstractItemView, QScrollArea, QWidget, QVBoxLayout, QComboBox, QHBoxLayout, QLabel, \
    QMessageBox
from qtpy import uic
from libs.share import SI

class ComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ComboBox, self).__init__(parent)

    def wheelEvent(self, event):
        event.ignore() # 忽悠滚轮事件

class ImportDB:
    def __init__(self, data_dict, header, id):
        self.ui = uic.loadUi("importdb.ui")
        self.ui.buttonBox.accepted.connect(self.btn_ok)
        self.cbls = []
        self.cbrs = []
        self.data_dict = data_dict
        self.header = header
        self.id = id

        container = QWidget()
        label1 = QLabel("源数据属性")
        label2 = QLabel("数据库字段")
        layout = QHBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        container.setLayout(layout)
        self.ui.VLayout.addWidget(container)

        self.scroll_area = QScrollArea() # 创建滚动区域
        self.scroll_widget = QWidget() # 创建滚动区域的内部部件
        self.scroll_layout = QVBoxLayout(self.scroll_widget) # 创建滚动区域的布局

        for i in range(len(header)):
            cbl = ComboBox()
            label = QLabel(header[i])
            for k, v in data_dict.items():
                cbl.addItem(k) # 源数据
            cbl.addItem('-')
            cbl.setCurrentText('-')
            self.cbls.append(cbl)
            container = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(cbl)
            layout.addWidget(label)
            container.setLayout(layout)
            self.scroll_layout.addWidget(container)

        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.ui.VLayout.addWidget(self.scroll_area)

    def btn_ok(self):
        S = set()
        for i in range(len(self.cbls)):
            text = self.cbls[i].currentText()
            if(text != '-' and text not in S):
                S.add(text)
            elif (text != '-'):
                QMessageBox.critical(
                    self.ui,
                    '错误',
                    '你重复导入了一列属性，请核实后重新导入！'
                )
                break
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='123456',
            db='geo',
            charset='utf8'
        )
        cursor = connection.cursor()
        id = self.id
        if id == -2: # 重
            for i in range(len(self.data_dict[self.cbls[0].currentText()])):
                data = []
                for j in range(len(self.cbls)):
                    if self.cbls[j].currentText() == '-':
                        data.append('-')
                    else:
                        data.append(self.data_dict[self.cbls[j].currentText()][i])
                sql = 'INSERT INTO gravity_data(Filename, Line_no, Flight_ID, Lon, Lat, x, y, Height_WGS1984, Date, Time, ST, CC, RB, XACC, LACC, Still, Base, ST_real, Beam_vel, rec_grav, Abs_grav, VaccCor, EotvosCor, FaCor, HaccCor, Free_air, FAA_filt, FAA_clip, Level_cor, FAA_level, Fa_4600m) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, tuple(data))
            connection.commit()
            connection.close()
        if id == -3: # 磁
            for i in range(len(self.data_dict[self.cbls[0].currentText()])):
                data = []
                for j in range(len(self.cbls)):
                    if self.cbls[j].currentText() == '-':
                        data.append('-')
                    else:
                        data.append(self.data_dict[self.cbls[j].currentText()][i])
                sql = 'INSERT INTO magnetic_data(Filename, Line_name, point, lon, lat, x, y, Height_WGS1984, Date, MagR, Magc, RefField, MagRTC, BCorr, MagBRTC, ACorr, MagF, MagL, MagML, MagML_Drape) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, tuple(data))
            connection.commit()
            connection.close()
        if id == -4: # 电
            for i in range(len(self.data_dict[self.cbls[0].currentText()])):
                data = []
                for j in range(len(self.cbls)):
                    if self.cbls[j].currentText() == '-':
                        data.append('-')
                    else:
                        data.append(self.data_dict[self.cbls[j].currentText()][i])
                sql = 'INSERT INTO electro_data(opnum, freq, comp, ampa, emag, ephz, hmag, hphz, resistivity, phase, rho, phz, Filename) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, tuple(data))
            connection.commit()
            connection.close()
        if id == -5: # 震
            for i in range(len(self.data_dict[self.cbls[0].currentText()])):
                data = []
                for j in range(len(self.cbls)):
                    if self.cbls[j].currentText() == '-':
                        data.append('-')
                    else:
                        data.append(self.data_dict[self.cbls[j].currentText()][i])
                sql = 'INSERT INTO seg_data(Filename, opnum, olnum, ns, dt, e, n, ampl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, tuple(data))
            connection.commit()
            connection.close()
        if id == -6: # 放
            for i in range(len(self.data_dict[self.cbls[0].currentText()])):
                data = []
                for j in range(len(self.cbls)):
                    if self.cbls[j].currentText() == '-':
                        data.append('-')
                    else:
                        data.append(self.data_dict[self.cbls[j].currentText()][i])
                sql = 'INSERT INTO gama_data(Fliename, Lon, Lat, kc, thc, uc) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, tuple(data))
            connection.commit()
            connection.close()
        if id == -7: # gps
            for i in range(len(self.data_dict[self.cbls[0].currentText()])):
                data = []
                for j in range(len(self.cbls)):
                    if self.cbls[j].currentText() == '-':
                        data.append('-')
                    else:
                        data.append(self.data_dict[self.cbls[j].currentText()][i])
                sql = 'INSERT INTO gps_data(Filename, FH, UCTCT, Lon, Lat, Vel, UTCD) VALUES (%s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, tuple(data))
            connection.commit()
            connection.close()
        if id == -8: # 高光谱
            for i in range(len(self.data_dict[self.cbls[0].currentText()])):
                data = []
                for j in range(len(self.cbls)):
                    if self.cbls[j].currentText() == '-':
                        data.append('-')
                    else:
                        data.append(self.data_dict[self.cbls[j].currentText()][i])
                sql = 'INSERT INTO hyper_data(Filename, content, description, samples, lines, bands, type, len) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, tuple(data))
            connection.commit()
            connection.close()
        if id == -9: # 地基合成孔径雷达
            for i in range(len(self.data_dict[self.cbls[0].currentText()])):
                data = []
                for j in range(len(self.cbls)):
                    if self.cbls[j].currentText() == '-':
                        data.append('-')
                    else:
                        data.append(self.data_dict[self.cbls[j].currentText()][i])
                sql = 'INSERT INTO sar_data(Filename, content, size, type, direction, proj) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, tuple(data))
            connection.commit()
            connection.close()
class Data_Table:
    def __init__(self):
        self.ui = uic.loadUi('data_table.ui')
        self.ui.table.horizontalHeader().setSectionsMovable(True)
        self.ui.table.horizontalHeader().setDragEnabled(True)
        self.ui.table.setSelectionBehavior(QAbstractItemView.SelectColumns)
        self.ui.table.setDragDropMode(QAbstractItemView.InternalMove)
        self.ui.btnData.clicked.connect(self.importDataBase)

    def importDataBase(self):
        model = self.ui.table.model()
        data_dict = {}
        if model is not None:
            for col in range(model.columnCount()):
                column_name = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
                column_data = []
                for row in range(model.rowCount()):
                    index = model.index(row, col)
                    data = model.data(index, Qt.DisplayRole)
                    column_data.append(data)
                data_dict[column_name] = column_data

        id = self.ui.buttonGroup.checkedId()
        # 从左到右分别是-2 -3 -4 -5 -6 -7 -8 -9
        header = []
        if id == -2:
            header = ['Filename', 'Line_no', 'Flight_ID', 'Lon', 'Lat', 'x', 'y', 'Height_WGS1984', 'Date', 'Time', 'ST', 'CC', 'RB',
                      'XACC', 'LACC', 'Still', 'Base', 'ST_real', 'Beam_vel', 'rec_grav', 'Abs_grav', 'VaccCor', 'EotvosCor', 'FaCor',
                      'HaccCor', 'Free air', 'FAA_flit', 'FAA_clip', 'Level_cor', 'FAA_level', 'Fa_4600m']
        if id == -3:
            header = ['Filename', 'Line_name', 'point', 'lon', 'lat', 'x', 'y', 'Height_WGS1984', 'Date', 'MagR', 'Magc', 'RefField',
                      'MagRTC', 'BCorr', 'MagBRTC', 'ACorr', 'MagF', 'MagL', 'MagML', 'MagML_Drape']
        if id == -4:
            header = ['Filename', 'opnum', 'freq', 'comp', 'ampa', 'emag', 'ephz', 'hmag', 'hphz', 'resistivity', 'phase', 'rho', 'phz']
        if id == -5:
            header = ['Filename', 'opnum', 'olnum', 'ns', 'dt', 'e', 'n', 'ampl']
        if id == -6:
            header = ['Filename', 'Lon', 'Lat', 'kc', 'thc', 'uc']
        if id == -7:
            header = ['Filename', 'FH', 'UCTCT', 'Lon', 'Lat', 'Vel', 'UTCD']
        if id == -8:
            header = ['Filename', 'content', 'description', 'samples', 'lines', 'bands', 'type', 'len']
        if id == -9:
            header = ['Filename', 'content', 'size', 'type', 'direction', 'proj']

        SI.dataWin = ImportDB(data_dict, header, id)
        SI.dataWin.ui.show()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasFormat("application/x-qabstractitemmodeldatalist"):
            encoded_data = mime_data.data("application/x-qabstractitemmodeldatalist")
            stream = QDataStream(encoded_data, QIODevice.ReadOnly)
            rows = []
            while not stream.atEnd():
                row, col, item_data = stream.readInt(), stream.readInt(), QByteArray()
                stream >> item_data
                rows.append((row, col, item_data))
            rows.sort(reverse=True)
            model = self.ui.table.model()
            for row, col, item_data in rows:
                if col != self.ui.table.horizontalHeader().currentIndex().column():
                    continue
                # 首先保存被拖拽的列的数据和列名
                old_col_data = []
                for i in range(model.rowCount()):
                    old_col_data.append(model.index(i, col).data())
                old_col_name = self.model().headerData(col, Qt.Horizontal, Qt.DisplayRole)

                # 移动列并修改列名
                self.horizontalHeader().moveSection(col, self.horizontalHeader().currentIndex().column())
                self.model().setHeaderData(self.horizontalHeader().currentIndex().column(), Qt.Horizontal, old_col_name, Qt.DisplayRole)

                # 将原来被拖拽的列的数据插入到新位置，由于前面已经移动了位置，所以使用当前列号
                for i, data in enumerate(old_col_data):
                    new_item = QStandardItem(str(data))
                    model.setItem(i, self.horizontalHeader().currentIndex().column(), new_item)
        else:
            self.ui.dropEvent(event)