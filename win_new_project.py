import json
from threading import Thread

from PyQt5.QtWidgets import QFileDialog
from qtpy import uic

from libs.share import MySignals

gms = MySignals()

class New_Project:
    def __init__(self):
        self.ui = uic.loadUi('new_project.ui')
        self.ui.choose_location.clicked.connect(self.chooseLocation)
        self.ui.btn_ok.clicked.connect(self.onOk)
        self.ui.btn_cancel.clicked.connect(self.onCancel)

    def chooseLocation(self):
        filePath = QFileDialog.getExistingDirectory(self.ui, "选择存储路径")
        self.ui.project_location.setText(filePath)

    def onOk(self):
        import os
        def threadFunc():
            name = self.ui.project_name.text()
            location = self.ui.project_location.text()
            project = '{}/{}'.format(location,name)
            os.makedirs(project,exist_ok=True)
            os.makedirs(project + "/" + "原始文件", exist_ok=True)
            jsonItem = {}
            jsonItem["name"] = name
            jsonItem["location"] = location
            jsonItem["project"] = project
            with open('category.json', 'r', encoding='utf8') as f:
                jsonStr = f.read()
            jsonData = json.loads(jsonStr)
            jsonData.append(jsonItem)
            jsonStr = json.dumps(jsonData,ensure_ascii=False,indent=2)
            with open('category.json', 'w', encoding='utf8') as f:
                f.write(jsonStr)
            gms.project.emit()
        Thread(target=threadFunc).start()
        self.ui.close()

    def onCancel(self):
        self.ui.close()