import pickle
import sys
import traceback
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QVBoxLayout, QScrollArea, QWidget, QMessageBox
from pathlib import Path
from qtpy import uic
from utils.pythonHighlighter import PythonHighlighter
from utils.codeEditor import QCodeEditor
from utils.toLog import StreamToQPlainTextEdit
class EditPluginWin:
    def __init__(self, classname):
        self.ui = uic.loadUi("edit_plugin.ui")
        with open('select_data.pkl', 'rb') as f:
            self.df = pickle.load(f)
        self.checkboxes = []
        self.classname = classname

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

        self.ui.gbl.setLayout(glayout)
        self.content_edit = QCodeEditor(display_line_numbers=True,
                                   highlight_current_line=True,
                                   syntax_high_lighter=PythonHighlighter)

        fixed_code = f"""# 插件类
class {classname}:
    # 初始化数据
    def __init__(self):
        self.model = None
    
    # 导入数据
    def set_model(self, model):
        self.model = model
        
    # 编写插件核心执行方法
    def run(self):
        pass
     
{classname} = {classname}()
{classname}.set_model(self.model)  # 使用外部的 self.model 初始化插件实例的 model 属性
{classname}.run()
        """

        self.content_edit.setPlainText(fixed_code)

        self.ui.btnrun.clicked.connect(self.run_code)
        self.ui.btninstall.clicked.connect(self.install_plugin)
        self.ui.codegb.layout().addWidget(self.content_edit.number_bar)
        self.ui.codegb.layout().addWidget(self.content_edit)
        self.ui.log.setReadOnly(True)
        sys.stdout = StreamToQPlainTextEdit(self.ui.log)
        self.model = None
        self.ui.show()

    def on_checkbox_state_changed(self):
        self.update_dataframe(self.get_selected_checkboxes_text())

    def get_selected_checkboxes_text(self):
        return [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]

    def update_dataframe(self, selected_columns):
        self.model = self.df[selected_columns].copy()

    def run_code(self):
        code = self.content_edit.toPlainText()
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

    def install_plugin(self):
        filename = f"{self.classname}.py"
        path = Path("./plugins")/filename
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(self.content_edit.toPlainText())
            QMessageBox.information(
                self.ui,
                "安装提示",
                f'插件{self.classname}已安装成功'
            )