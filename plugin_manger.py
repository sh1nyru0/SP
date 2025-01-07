import os
import pickle
import shutil
import traceback

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QScrollArea, QWidget, QCheckBox, QMessageBox, QFileDialog
from pathlib import Path
from qtpy import uic


class PluginMangerWin:
    def __init__(self):
        self.ui = uic.loadUi("plugin_manger.ui")
        with open('select_data.pkl', 'rb') as f:
            self.df = pickle.load(f)
        self.checkboxes = []
        self.plugins = self.get_all_filenames_without_extension('./plugins')
        self.ui.btnuse.clicked.connect(self.run)
        self.ui.btndelete.clicked.connect(self.delete)
        self.ui.btninstall.clicked.connect(self.install)

        self.ui.cbuse.addItems(self.plugins)
        self.ui.cbdelete.addItems(self.plugins)

        # 创建 QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 确保内容可以调整大小

        glayout = QVBoxLayout()
        # 创建容器小部件并设置其布局
        container_widget = QWidget()
        vlayout = QVBoxLayout(container_widget)

        all_columns = self.df.columns
        for i in range(len(all_columns)):
            hlayout = QHBoxLayout()
            check = QCheckBox(self.df.columns[i])
            check.stateChanged.connect(self.on_checkbox_state_changed)
            self.checkboxes.append(check)
            hlayout.addWidget(check)
            vlayout.addLayout(hlayout)
        scroll_area.setWidget(container_widget)

        glayout.addWidget(scroll_area)

        self.ui.groupBox.setLayout(glayout)

    def on_checkbox_state_changed(self):
        self.update_dataframe(self.get_selected_checkboxes_text())

    def update_dataframe(self, selected_columns):
        self.model = self.df[selected_columns].copy()

    def get_selected_checkboxes_text(self):
        return [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]

    def get_all_filenames_without_extension(self, directory):
        filenames = []
        path = Path(directory)

        if not path.is_dir():
            raise NotADirectoryError(f"'{directory}' is not a valid directory.")

        # 使用 rglob 来递归获取所有文件
        for file_path in path.rglob('*'):
            if file_path.is_file():
                # 去掉文件扩展名并添加到列表
                filenames.append(file_path.stem)

        return filenames

    def run(self):
        item = self.ui.cbuse.currentText()
        path = f'./plugins/{item}.py'
        with open(path, 'r', encoding='utf-8') as file:
            code = file.read()
        try:
            local_vars = {'self': self}
            exec(code, globals(), locals())
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            error_message = f"Error: {e}\n"
            user_frames = [frame for frame in tb if frame.filename == '<string>']
            for frame in user_frames:
                filename, lineno, function, line = frame
                error_message += f"  File \"{filename}\", line {lineno}, in {function}\n    {line}\n"
            print(error_message)

    def delete(self):
        item = self.ui.cbdelete.currentText()
        path = f'./plugins/{item}.py'
        os.remove(path)
        QMessageBox.information(
            self.ui,
            "删除提示",
            f'插件{item}已删除！'
        )
        self.plugins = self.get_all_filenames_without_extension('./plugins')
        self.ui.cbuse.clear()
        self.ui.cbdelete.clear()
        self.ui.cbuse.addItems(self.plugins)
        self.ui.cbdelete.addItems(self.plugins)

    def install(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self.ui,
            "安装插件",
            "",
            "Python Files (*.py);;All Files (*)",
            options=options
        )
        shutil.copy(filePath, './plugins')
        QMessageBox.information(
            self.ui,
            "安装提示",
            f'插件{Path(filePath).stem}安装成功！'
        )
        self.plugins = self.get_all_filenames_without_extension('./plugins')
        self.ui.cbuse.clear()
        self.ui.cbdelete.clear()
        self.ui.cbuse.addItems(self.plugins)
        self.ui.cbdelete.addItems(self.plugins)