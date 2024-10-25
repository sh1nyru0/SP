import json
import os
import re
import shutil
from threading import Thread
import lasio
import numpy as np
import pandas as pd
import pymysql
import segyio
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QInputDialog, QLineEdit, QMessageBox, QFileDialog, QTreeWidgetItem, QMdiSubWindow, \
    QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, QPushButton, QComboBox
from qtpy import uic

from GridWin import GridWin
# from data_table import Data_Table
from db import DB
from libs.share import MySignals, SI
from original_data import Original_Data
from pandas_model import PandasModel
from preview_csv import Preview_CSV
from preview_data import Preview_Data
from welcome import Welcome
from win_gramag_setting import WinGraMagSetting
from win_new_project import New_Project
from win_seismic_setting import WinSeismicSetting

gms = MySignals()

gpslist = ['Filename', 'FH', 'UCTCT', 'Lon', 'Lat', 'Vel', 'UTCD', 'xq', 'yq', 'zq', 'gridname']
electrolist = ['Filename', 'opnum', 'freq', 'comp', 'ampa', 'emag', 'ephz', 'hmag', 'hphz', 'resistivity', 'phase', 'rho', 'phz', 'xq', 'yq', 'zq', 'gridname']
gamalist = ['Filename', 'Lon', 'Lat', 'kc', 'thc', 'uc', 'xq', 'yq', 'zq', 'gridname']
gravitylist = ['Filename', 'Line_no', 'Flight_ID', 'Lon', 'Lat', 'x', 'y', 'Height_WGS1984', 'Date', 'Time', 'ST', 'CC', 'RB', 'XACC', 'LACC', 'Still', 'Base', 'ST_real', 'Beam_vel', 'rec_grav', 'Abs_grav', 'VaccCor', 'EotvosCor', 'FaCor', 'HaccCor', 'Free_air', 'FAA_filt', 'FAA_clip', 'Level_cor', 'FAA_level', 'Fa_4600m', 'xq', 'yq', 'zq', 'gridname']
hyperlist = ['Filename', 'content', 'description', 'samples', 'lines', 'bands', 'type', 'len', 'xq', 'yq', 'zq', 'gridname']
magneticlist = ['Filename', 'Line_name', 'point', 'lon', 'lat', 'x', 'y', 'Height_WGS1984', 'Date', 'MagR', 'Magc', 'RefField', 'MagRTC', 'BCorr', 'MagBRTC', 'ACorr', 'MagF', 'MagL', 'MagML', 'MagML_Drape', 'xq', 'yq', 'zq', 'gridname']
sarlist = ['Filename', 'content', 'size', 'type', 'direction', 'proj', 'xq', 'yq', 'zq', 'gridname']
seglist = ['Filename', 'opnum', 'olnum', 'ns', 'dt', 'e', 'n', 'ampl', 'xq', 'yq', 'zq', 'gridname']
lists = ['-', gpslist, sarlist, seglist, gamalist, electrolist, magneticlist, gravitylist, hyperlist]
datanames = ['-', 'gps_data', 'sar_data', 'seg_data', 'gama_data', 'electro_data', 'magnetic_data', 'gravity_data', 'hyper_data']
cdatanames = ['-', 'gps数据', '地基合成孔径雷达数据', '地震数据', '放射性数据', '电法数据', '磁法数据', '重力数据', '高光谱数据']

class Win_Start:
    def __init__(self):
        self.ui = uic.loadUi('start.ui')
        self.ui.new_project.clicked.connect(self.newProject)
        self.ui.btn_cancel.clicked.connect(self.onCancel)
        self.ui.btn_ok.clicked.connect(self.onOk)
        self.readProject()
        gms.project.connect(self.readProject)

    def readProject(self):
        with open('category.json', encoding='utf8') as f:
            jsonStr = f.read()
        jsonData = json.loads(jsonStr)
        self.ui.choose_project.clear()
        for i in range(len(jsonData)):
            self.ui.choose_project.addItem(jsonData[i]["project"])

    def newProject(self):
        SI.newProjectWin = New_Project()
        SI.newProjectWin.ui.show()

    def onOk(self):
        SI.mainWin = Win_Main(self.ui.choose_project.currentText())
        SI.mainWin._openSubWin(Welcome,connection=None)
        SI.mainWin.ui.show()
        def threadFunc():
            path = self.ui.choose_project.currentText()
            SI.currentProject = path
            name = os.path.basename(path)
            gms.projectFile.emit(path, name)

        Thread(target=threadFunc).start()
        self.ui.close()

    def onCancel(self):
        self.ui.close()

class Win_Filter:
    def __init__(self, projectPath, filePath, fileName, connection):
        self.ui = uic.loadUi("filter_data.ui")
        self.columns = []
        self.checkboxes = []
        self.cbs = []
        self.btns = []
        self.dataname = None
        self.projectPath = projectPath
        self.filePath = filePath
        self.df = None
        self.fileName = fileName
        self.connection = connection
        self.ui.btnLoadData.clicked.connect(self.onLoadData)
        self.ui.btnCancel.clicked.connect(self.onCancel)
        self.ui.datacb.currentIndexChanged.connect(self.chooseDataBase)

    # 1 gps 2 雷达 3 地震 4 放射性 5 电法 6 磁法  7 重力 8 高光谱
    def chooseDataBase(self,index):
        filePath = self.filePath
        self.dataname = datanames[index]
        if self.filePath.lower().endswith('.xyz'):
            df = self.read_xyz(filePath)
        elif filePath.lower().endswith('.las'):
            df = self.read_las(filePath)
        elif filePath.lower().endswith('.grd'):
            df = self.read_grd(filePath)
        elif filePath.lower().endswith('.csv'):
            df = self.read_csv(filePath)
        elif filePath.lower().endswith('.txt'):
            df = self.read_txt(filePath)
        elif filePath.lower().endswith('.sgy'):
            df = self.read_sgy(filePath)
        elif filePath.lower().endswith('.edi'):
            df = self.read_edi(filePath)
        elif filePath.lower().endswith('.nc'):
            df = self.read_nc(filePath)
        elif filePath.lower().endswith('.las'):
            df = self.read_las(filePath)
        column_names = df.columns.tolist()
        self.df = df.iloc[int(self.ui.rowInput.text()):]
        gms.filterdf.emit(self.df, self.dataname, self.fileName)

        # 检查是否已经有 scroll_area，并移除它
        if hasattr(self, 'scroll_area') and self.scroll_area is not None:
            # 从布局中移除旧的 scroll_area
            self.ui.columnLayout.removeWidget(self.scroll_area)
            # 删除旧的 scroll_area 以释放资源
            self.scroll_area.deleteLater()

        self.scroll_area = QScrollArea()  # 创建滚动区域
        self.scroll_widget = QWidget()     # 创建滚动区域的内部部件
        self.scroll_layout = QVBoxLayout(self.scroll_widget)  # 创建滚动区域的布局

        lists = ['-', gpslist, sarlist, seglist, gamalist, electrolist, magneticlist, gravitylist, hyperlist]
        if index > 0:
            for i, name in enumerate (lists[index]):
                container = QWidget()
                layout = QHBoxLayout()
                label = QLabel(name)
                cb = QComboBox()
                cb.addItems(column_names)
                cb.addItem('-')
                layout.addWidget(label)
                layout.addWidget(cb)
                container.setLayout(layout)
                self.scroll_layout.addWidget(container)
                self.cbs.append(cb)

        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.ui.columnLayout.addWidget(self.scroll_area)

    # 加载数据按钮(直接将所选数据导入数据库)
    def onLoadData(self):
        index = self.ui.datacb.currentIndex()
        columns = lists[index]
        columns_str = ','.join(columns)
        cursor = self.connection.cursor()
        # 插入所选数据
        placeholders = ",".join(["%s"] * len(columns))
        sql = f'INSERT INTO {self.dataname}({columns_str}) VALUES({placeholders})'
        for i in range(self.df.shape[0]):
            rowdata = self.df.iloc[i]
            values = []
            for j in range(len(self.cbs)):
                values.append(rowdata[self.cbs[j].currentText()])
            cursor.execute(sql, tuple(values))
        self.connection.commit()
        # 查找所选文件名的数据
        SI.mainWin._openSubWin(DB, connection=self.connection, tableid=index, filename= self.fileName)
        # 在数据表里创建文件夹并且刷新文件树
        path = self.projectPath + "/" + cdatanames[index] + "/" + self.fileName
        os.makedirs(path, exist_ok=True)
        self.ui.close()
        gms.projectFile.emit(self.projectPath,
                             os.path.basename(self.projectPath))

    def onCancel(self):
        self.ui.close()


    def read_nc(self, filePath, skip_rows=0, selected_clumns=None):
        import numpy as np
        from osgeo import gdal
        from netCDF4 import Dataset
        dir = filePath
        # 获取nc文件的内部变量
        nc = Dataset(dir)
        # 定义一个DataFrame()存储变量值
        df = pd.DataFrame()
        # 循环获取nc中的各个变量，并且把变量的值读出
        for var in nc.variables.keys():
            # 构建变量的路径
            variable_path = 'NETCDF:' + dir + ':' + var
            # 打开变量
            variable = gdal.Open(variable_path)
            # 检查变量是否成功打开
            if variable is not None:
                # 获取变量值
                variable_value = variable.ReadAsArray()

                # 检查变量值是否为 None
                if variable_value is not None:
                    # 将多维数组变成一维
                    variable_value_flat = variable_value.flatten('C')
                    # 将变量和值写入到 DataFrame 中
                    df[var] = pd.Series(variable_value_flat)
                else:
                    df[var] = np.nan
            else:
                continue
        df.insert(0, 'Filename', self.fileName)
        return df

    def read_edi(self, filePath, skip_rows=0, selected_clumns=None):
        with open(filePath, 'r') as file:
            edi_content = file.readlines()[65:]
            freq_data = {}
        # 处理每行数据
        key = ""
        for line in edi_content:
            fields = line.strip()
            # 打印解析后的字段值
            if line.startswith('>') and not line.startswith('>!'):
                if fields == ">END":
                    break
                key = fields.lstrip().lstrip('>').split('//')[0].strip()
                freq_data[key] = []
            elif key != "" and fields != "" and not line.startswith('>!'):
                values = fields.split('  ')
                for i in range(len(values)):
                    freq_data[key].append(float(values[i]))
        fieldnames = freq_data.keys()
        data = [{key: values[i] for key, values in freq_data.items()} for i in
                range(len(list(freq_data.values())[0]))]
        df = pd.DataFrame(data, columns=fieldnames)
        df.insert(0, 'Filename', self.fileName)
        return df

    def read_sgy(self, filepath, skip_rows=0, selected_columns=None):
        data = segyio.open(filepath)
        headers = segyio.tracefield.keys
        df = pd.DataFrame(columns=list(headers.keys()))
        for header_name, byte in headers.items():
            df[header_name] = data.attributes(byte)[:]
        inline_no = df['INLINE_3D']
        xline_no = df['CROSSLINE_3D']
        df['i'] = inline_no - inline_no.min()
        df['j'] = xline_no - xline_no.min()
        df.insert(0, 'Filename', self.fileName)
        return df

    def read_las(self, file_path, skip_rows=0, selected_columns=None):
        las = lasio.read(file_path)
        df = las.df()
        df.reset_index(inplace=True)
        if selected_columns:
            available_columns = df.columns.intersection(selected_columns)
            df = df[available_columns]
        if skip_rows > 0:
            df = df.iloc[skip_rows:]
        df.insert(0, 'Filename', self.fileName)
        return df

    def read_csv(self, file_path, skip_rows=0, selected_columns=None):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        column_names = lines[0].rstrip('\n').split(',')
        data = [line.rstrip('\n').split(',') for line in lines[1 + skip_rows:]]
        # 填充缺失的数据为 NaN
        for row in data:
            if len(row) < len(column_names):
                row += [np.nan] * (len(column_names) - len(row))
                # 创建 DataFrame，并将数据转换为数值类型
        df = pd.DataFrame(data, columns=column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        if selected_columns:
            df = df[selected_columns]
        df.insert(0, 'Filename', self.fileName)
        return df


    def read_xyz(self, file_path, skip_rows=0, selected_columns=None):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            all_column_names = re.split(r'\s+', lines[5].strip())[1:]  # 第9行包含列名
        usecols = selected_columns if selected_columns else all_column_names
        df = pd.read_csv(file_path, sep='\s+', skiprows=skip_rows + 8, names=all_column_names, usecols=usecols,
                         engine='python')
        df.insert(0, 'Filename', self.fileName)
        return df

    def read_grd(self, file_path, skip_rows=0, selected_columns=None):
        data = []
        max_cols = 0
        with open(file_path, 'r') as file:
            for _ in range(6 + skip_rows):
                next(file)
            for line in file:
                cols = line.strip().split()
                max_cols = max(max_cols, len(cols))
                data.append(cols)
        for i, row in enumerate(data):
            if len(row) < max_cols:
                data[i].extend([None] * (max_cols - len(row)))
        df = pd.DataFrame(data, columns=[f'第{i + 1}列' for i in range(max_cols)])
        if selected_columns:
            df = df[selected_columns]
        df.insert(0, 'Filename', self.fileName)
        return df

    def read_txt(self, file_path, skip_rows=0, selected_columns=None):
        with open(file_path, 'r') as file:
            lines = file.readlines()
        column_names = lines[0].split()
        data = [line.split() for line in lines[1 + skip_rows:]]
        # 填充缺失的数据为 NaN
        for row in data:
            if len(row) < len(column_names):
                row += [np.nan] * (len(column_names) - len(row))
        # 创建 DataFrame，并将数据转换为数值类型
        df = pd.DataFrame(data, columns=column_names)
        df = df.apply(pd.to_numeric, errors='ignore')
        if selected_columns:
            df = df[selected_columns]
        df.insert(0, 'Filename', self.fileName)
        return df

class Win_Main:
    def __init__(self, projectpath):
        self.ui = uic.loadUi("main.ui")
        self.ui.actionNewProject.triggered.connect(self.onNewProject)
        self.ui.actionOpenProject.triggered.connect(self.onOpenProject)
        self.ui.actiondataExport.triggered.connect(self.onDataExport)
        self.ui.actiondataImport.triggered.connect(self.onDataImport)
        self.ui.actiondataPreview.triggered.connect(self.onDataPreview)
        self.ui.actionGrid.triggered.connect(self.onGrid)
        self.ui.actionSeismic.triggered.connect(self.seismic)
        self.ui.actionGraMag.triggered.connect(self.graMag)
        self.ui.fileTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.fileTree.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.ui.fileTree.customContextMenuRequested.connect(self.showContextMenu)
        self.projectpath = projectpath
        self.projectname = os.path.basename(projectpath)

        self.connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='123456',
            db=self.projectname,
            charset='utf8'
        )

        gms.projectFile.connect(self.loadProject)
        gms.loadData.connect(self.loadData)
        self.mainPath = None # 项目路径
        self.currentPath = None # 树形图中当前路径
        self.model = None

    def __del__(self):
        self.connection.close()
     # 网格化
    def onGrid(self):
        SI.gridWin = GridWin(self.connection, self.model, self.currentPath)
        SI.gridWin.ui.show()

    def showContextMenu(self, pos):
        item = self.ui.fileTree.itemAt(pos)
        project = "/".join(SI.currentProject.split("/")[:-1])
        path = ""
        idx = item
        while idx is not None:
            path = idx.text(0) + "/" + path
            idx = idx.parent()
        path = path.rstrip("/")
        path = project + "/" + path
        if item is None:
            return
        if not os.path.isdir(path):
            # 文件菜单
            menuFile = QMenu(self.ui.fileTree)
            actFileOpen = menuFile.addAction("打开")
            actFileRename = menuFile.addAction("重命名")
            actFileCopy = menuFile.addAction("另存为")
            actFileDelete = menuFile.addAction("删除")
            if os.path.basename(os.path.dirname(path)) == "原始文件":
                actDataImport = menuFile.addAction("数据导入")
                actDataImport.triggered.connect(lambda: self.actDataImport(path))
            actFileOpen.triggered.connect(lambda: self.actFileOpen(path))
            actFileRename.triggered.connect(lambda: self.actFileRename(path))
            actFileCopy.triggered.connect(lambda: self.actFileCopy(path))
            actFileDelete.triggered.connect(lambda: self.actFileDelete(path))
            # 在指定位置显示菜单
            menuFile.exec_(self.ui.fileTree.mapToGlobal(pos))

        else:
            # 文件夹菜单
            menuFolder = QMenu(self.ui.fileTree)
            actFolderRename = menuFolder.addAction("重命名")
            actFolderDelete = menuFolder.addAction("删除")

            actFolderRename.triggered.connect(lambda: self.actFolderRename(path))
            actFolderDelete.triggered.connect(lambda: self.actFolderDelete(path))
            if path == self.mainPath:
                # 在指定位置显示菜单
                menuFolder.exec_(self.ui.fileTree.mapToGlobal(pos))

    def actFolderRename(self, path):
        if path == self.mainPath:
            title, okPressed = QInputDialog.getText(
                self.ui,
                "主项目重命名",
                "请输入修改后的主项目名称:",
                QLineEdit.Normal,
                os.path.basename(path))
            if not okPressed:
                return
            newDir = '{}/{}'.format(os.path.dirname(path), title)
            with open('category.json', 'r') as f:
                jsonStr = f.read()
            jsonData = json.loads(jsonStr)
            for i in range(len(jsonData)):
                if jsonData[i]['project'] == self.mainPath:
                    jsonData[i] = {'name': title, 'location': os.path.dirname(path), 'project': newDir}
            with open('category.json', 'w') as f:
                f.write(json.dumps(jsonData))
            os.rename(path, newDir)
            gms.projectFile.emit(newDir, title)
        else:
            title, okPressed = QInputDialog.getText(
                self.ui,
                "目录重命名",
                "请输入修改后的目录名:",
                QLineEdit.Normal,
                os.path.basename(path))
            if not okPressed:
                return
            newDir = os.path.join(os.path.dirname(path), title)
            os.rename(path, newDir)
            self.loadProject(self.mainPath, os.path.basename(self.mainPath))

    def actFolderDelete(self, path):
        if path == self.mainPath:
            choice = QMessageBox.question(
                self.ui,
                '确认',
                '确定要删除主项目{}吗？'.format(os.path.basename(path)))
            if choice == QMessageBox.Yes:
                with open('category.json', 'r') as f:
                    jsonStr = f.read()
                jsonData = json.loads(jsonStr)
                try:
                    for i in range(len(jsonData)):
                        if jsonData[i]['project'] == self.mainPath:
                            del (jsonData[i])
                except Exception as e:
                    pass
                with open('category.json', 'w') as f:
                    f.write(json.dumps(jsonData))
                shutil.rmtree(self.mainPath, ignore_errors=True)
                SI.startWin = Win_Start()
                SI.startWin.ui.show()
                self.ui.close()
            if choice == QMessageBox.No:
                return
        else:
            choice = QMessageBox.question(
                self.ui,
                '确认',
                '确定要删除文件夹{}吗？'.format(os.path.basename(path)))
            if choice == QMessageBox.Yes:
                shutil.rmtree(path, ignore_errors=True)
                self.loadProject(self.mainPath, os.path.basename(self.mainPath))
            if choice == QMessageBox.No:
                return

    def actFileOpen(self,path):
        if not os.path.isdir(path):
            _, fileExtension = os.path.splitext(path)
            # 在MDI子窗口中打开该文件
            if fileExtension == ".csv":
                df = pd.read_csv(path)
                model = PandasModel(df)
                self._openSubWin(Data_Table)
                SI.subWinTable[str(Data_Table)]['subWin'].setWindowTitle(os.path.basename(path))
                SI.subWinTable[str(Data_Table)]['subWin'].widget().table.setModel(model)
            else:
                try:
                    df = pd.read_csv(path)
                    model = PandasModel(df)
                except Exception as e:
                    QMessageBox.critical(
                        self.ui,
                        '错误',
                        '该类格式无法直接读取，请进行格式转化！')
                    return
                self._openSubWin(Original_Data)
                SI.subWinTable[str(Original_Data)]['subWin'].setWindowTitle(os.path.basename(path))
                SI.subWinTable[str(Original_Data)]['subWin'].widget().list.setModel(model)
        else:
            return

    def actFileRename(self, path):
        title, okPressed = QInputDialog.getText(
            self.ui,
            "文件重命名",
            "请输入修改后的文件名称:",
            QLineEdit.Normal,
            os.path.splitext(os.path.basename(path))[0])
        if not okPressed:
            return
        dirname, filename = os.path.split(path)
        newPath = os.path.join(dirname, title + os.path.splitext(filename)[1])
        os.rename(path, newPath)
        self.loadProject(self.mainPath, os.path.basename(self.mainPath))

    def actFileCopy(self, path):
        filePath = QFileDialog.getExistingDirectory(self.ui, "选择存储路径")
        shutil.copy(path, os.path.join(filePath, os.path.basename(path)))

    def actFileDelete(self, path):
        choice = QMessageBox.question(
            self.ui,
            '确认',
            '确定要删除文件{}吗？'.format(os.path.basename(path)))
        if choice == QMessageBox.Yes:
            os.remove(path)
            self.loadProject(self.mainPath, os.path.basename(self.mainPath))
        if choice == QMessageBox.No:
            return

    def seismic(self):
        SI.seismicSettingWin = WinSeismicSetting()
        SI.seismicSettingWin.ui.show()

    def graMag(self):
        SI.graMagSettingWin = WinGraMagSetting()
        SI.graMagSettingWin.ui.show()

    # 加载数据生成表格
    def loadData(self, model):
        self._openSubWin(Data_Table)
        SI.subWinTable[str(Data_Table)]['subWin'].setWindowTitle("主数据窗口")
        SI.subWinTable[str(Data_Table)]['subWin'].widget().table.setModel(model)

    def savePreview(self, previewPath):
        _, fileExtension = os.path.splitext(previewPath)
        title, okPressed = QInputDialog.getText(
            self.ui,
            "输入文件名",
            "名称:",
            QLineEdit.Normal,
            os.path.splitext(os.path.basename(previewPath))[0])
        if not okPressed:
            return
        shutil.copyfile(previewPath, self.mainPath + "/原始文件/" + title + fileExtension)
        self.loadProject(self.mainPath, os.path.basename(self.mainPath))

    # 在操作树界面表中加载出项目文件夹
    def loadProject(self, path, name):
        # path是项目目录, name是项目的名称
        def loadFolder(path, parent_item):
            for file_name in os.listdir(path):
                file_path = os.path.join(path, file_name)
                if os.path.isdir(file_path):  # 判断是否是文件夹
                    folder_item = QTreeWidgetItem(parent_item, [file_name])
                    # 设置文件夹图标
                    folder_item.setIcon(0,QIcon("./images/文件夹.png"))
                    loadFolder(file_path, folder_item)
                else:  # 文件
                    file_item = QTreeWidgetItem(parent_item, [file_name])
                    file_item.setIcon(0,QIcon("./images/数据.png"))
        self.ui.fileTree.clear()

        self.mainPath = path
        rootFolder = path
        rootItem = QTreeWidgetItem(self.ui.fileTree, [name])
        rootItem.setIcon(0, QIcon("./images/文件夹.png"))
        loadFolder(rootFolder, rootItem)

    def onNewProject(self):
        SI.newProjectWin = New_Project()
        SI.newProjectWin.ui.show()

    def onOpenProject(self):
        SI.startWin = Win_Start()
        SI.startWin.ui.show()

    # 数据导出
    def onDataExport(self):
        def threadFunc():
            path = SI.currentProject
            name = os.path.basename(path)
            gms.projectFile.emit(path, name)
        path, _ = QFileDialog.getSaveFileName(self.ui, "Save File", SI.currentProject, "CSV (*.csv)")
        # 检查用户选择的文件路径是否在 SI.currentProject 范围内
        if not path.startswith(SI.currentProject):
            # 用户选择了不正确的路径，进行相应处理
            QMessageBox.critical(
                self.ui,
                '错误',
                '文件只能保存在主项目中，请重新选择保存路径！')
        else:
            if path:
                dataFrame = SI.subWinTable[str(Data_Table)]['subWin'].widget().table.model()._data
                dataFrame.to_csv(path, index=False)
            Thread(target=threadFunc).start()

    def onDataPreview(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择你要查看的文件",  # 标题
            "",  # 起始目录
            "文件类型 (*.las *.txt *.csv *.XYZ *.grd)"  # 选择类型过滤项，过滤内容在括号中
        )
        _, fileExtension = os.path.splitext(filePath)
        if fileExtension in ['.las', '.txt', '.XYZ', '.grd']:
            if filePath:
                df = pd.read_csv(filePath)
                model = PandasModel(df)
                self._openSubWin(Preview_Data, filePath)
                SI.subWinTable[str(Preview_Data)]['subWin'].setWindowTitle(os.path.basename(filePath))
                SI.subWinTable[str(Preview_Data)]['subWin'].widget().list.setModel(model)
        if fileExtension in ['.csv']:
            if filePath:
                df = pd.read_csv(filePath)
                model = PandasModel(df)
                self._openSubWin(Preview_CSV, filePath)
                SI.subWinTable[str(Preview_CSV)]['subWin'].setWindowTitle(os.path.basename(filePath))
                SI.subWinTable[str(Preview_CSV)]['subWin'].widget().table.setModel(model)

    def onDataImport(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择需要导入的文件",  # 标题
            "",  # 起始目录
            "文件类型 (*.sgy *.edi *.nc *.las *.XYZ *.csv *.grd *.txt)"  # 选择类型过滤项，过滤内容在括号中
        )
        _, fileExtension = os.path.splitext(filePath)
        if fileExtension in [".sgy", ".edi", ".nc", ".las", ".XYZ", ".csv", ".grd", ".txt"]:
            title, okPressed = QInputDialog.getText(
                self.ui,
                "请为转换后的文件命名",
                "名称:",
                QLineEdit.Normal,
                os.path.splitext(os.path.basename(filePath))[0])
            if okPressed:
                SI.filterWin = Win_Filter(self.projectpath, filePath,  title, self.connection)
                SI.filterWin.ui.show()


    def _openSubWin(self, FuncClass, connection=None, tableid=None, filename=None):
        def createOrUpdateSubWin():
            # 创建新子窗口实例
            subWinFunc = FuncClass(connection, tableid, filename)
            # 创建 QMdiSubWindow 并设置子控件
            subWin = QMdiSubWindow()
            subWin.setWidget(subWinFunc.ui)
            subWin.setAttribute(Qt.WA_DeleteOnClose)
            self.ui.mdiArea.addSubWindow(subWin)

            # 保存窗口引用
            SI.subWinTable[str(FuncClass)] = {'subWin': subWin, 'subWinFunc': subWinFunc}

            # 显示窗口并提到最上层
            subWin.setWindowState(Qt.WindowActive | Qt.WindowMaximized)
            subWin.show()
        # 检查该功能类型的实例是否已经存在
        if str(FuncClass) in SI.subWinTable:
            try:
                # 取出已经存在的窗口
                subWin = SI.subWinTable[str(FuncClass)]['subWin']
                # 检查窗口是否已被销毁
                if subWin is not None and subWin.isVisible():
                    # 关闭并彻底删除现有窗口
                    subWin.close()
                    subWin.deleteLater()
                    SI.subWinTable.pop(str(FuncClass), None)
            except RuntimeError:
                # 如果窗口已经被销毁，删除引用
                SI.subWinTable.pop(str(FuncClass), None)
        # 创建新的窗口
        createOrUpdateSubWin()

    def onItemDoubleClicked(self, item):
        project = "/".join(SI.currentProject.split("/")[:-1])
        path = ""
        idx = item
        while idx is not None:
            path = idx.text(0) + "/" + path
            idx = idx.parent()
        path = path.rstrip("/")
        path = project + "/" + path
        self.currentPath = path
        if not os.path.isdir(path):
            _, fileExtension = os.path.splitext(path)
            if fileExtension == '.csv':
                df = pd.read_csv(path)
                model = PandasModel(df)
                self._openSubWin(Data_Table)
                SI.subWinTable[str(Data_Table)]['subWin'].setWindowTitle(item.text(0))
                SI.subWinTable[str(Data_Table)]['subWin'].widget().table.setModel(model)
            else:
                try:
                    df = pd.read_csv(path)
                    model = PandasModel(df)
                except Exception as e:
                    print("异常为:",e)
                    QMessageBox.critical(
                        self.ui,
                        '错误',
                        '该类格式无法直接读取，请进行格式转化！')
                    return
                self._openSubWin(Original_Data)
                SI.subWinTable[str(Original_Data)]['subWin'].setWindowTitle(item.text(0))
                SI.subWinTable[str(Original_Data)]['subWin'].widget().list.setModel(model)
        else:
            if(os.path.basename(path) == "重力数据"):
                SI.mainWin._openSubWin(DB, connection=self.connection, tableid=7)
            if(os.path.basename(path) == "磁法数据"):
                SI.mainWin._openSubWin(DB, connection=self.connection, tableid=6)
            if(os.path.basename(path) == "电法数据"):
                SI.mainWin._openSubWin(DB, connection=self.connection, tableid=5)
            if(os.path.basename(path) == "地震数据"):
                SI.mainWin._openSubWin(DB, connection=self.connection, tableid=3)
            if(os.path.basename(path) == "gps数据"):
                SI.mainWin._openSubWin(DB, connection=self.connection, tableid=1)
            if(os.path.basename(path) == "放射性数据"):
                SI.mainWin._openSubWin(DB, connection=self.connection, tableid=4)
            if(os.path.basename(path) == "高光谱数据"):
                SI.mainWin._openSubWin(DB, connection=self.connection, tableid=8)
            if(os.path.basename(path) == "地基合成孔径雷达数据"):
                SI.mainWin._openSubWin(DB, connection=self.connection, tableid=2)
            else:
                pdir = os.path.basename(os.path.dirname(path)) #path的上一级目录
                if(pdir == "重力数据"):
                    SI.mainWin._openSubWin(DB, connection=self.connection, tableid=7, filename=os.path.basename(path))
                if(pdir == "磁法数据"):
                    SI.mainWin._openSubWin(DB, connection=self.connection, tableid=6, filename=os.path.basename(path))
                if(pdir == "电法数据"):
                    SI.mainWin._openSubWin(DB, connection=self.connection, tableid=5, filename=os.path.basename(path))
                if(pdir == "地震数据"):
                    SI.mainWin._openSubWin(DB, connection=self.connection, tableid=3, filename=os.path.basename(path))
                if(pdir == "gps数据"):
                    SI.mainWin._openSubWin(DB, connection=self.connection, tableid=1, filename=os.path.basename(path))
                if(pdir == "放射性数据"):
                    SI.mainWin._openSubWin(DB, connection=self.connection, tableid=4, filename=os.path.basename(path))
                if(pdir == "高光谱数据"):
                    SI.mainWin._openSubWin(DB, connection=self.connection, tableid=8, filename=os.path.basename(path))
                if(pdir == "地基合成孔径雷达数据"):
                    SI.mainWin._openSubWin(DB, connection=self.connection, tableid=2, filename=os.path.basename(path))
            self.model = SI.subWinTable[str(DB)]['subWin'].widget().table.model()