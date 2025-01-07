import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QComboBox, QScrollArea, QLabel

class ScrollableWidget(QWidget):
    def __init__(self, df_columns, all_columns):
        super().__init__()

        self.df_columns = df_columns
        self.all_columns = all_columns

        self.initUI()

    def initUI(self):
        # 创建主窗口的垂直布局
        main_layout = QVBoxLayout()

        # 创建 QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 确保内容可以调整大小

        # 创建容器小部件并设置其布局
        container_widget = QWidget()
        vlayout = QVBoxLayout(container_widget)

        # 动态添加复选框和组合框到水平布局中
        for i in range(len(self.df_columns)):
            hlayout = QHBoxLayout()
            check = QCheckBox(self.df_columns[i])  # 使用列名作为复选框标签
            combo = QComboBox()
            combo.addItems(self.all_columns)
            hlayout.addWidget(check)
            hlayout.addWidget(combo)
            vlayout.addLayout(hlayout)

        # 将容器小部件设置为 QScrollArea 的内容
        scroll_area.setWidget(container_widget)

        # 将 QScrollArea 添加到主窗口的布局中
        main_layout.addWidget(scroll_area)

        # 设置主窗口的布局
        self.setLayout(main_layout)

        # 设置窗口标题和大小
        self.setWindowTitle('带滚动条的布局示例')
        self.setGeometry(300, 300, 400, 300)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 示例数据
    df_columns = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5', 'Column6', 'Column7', 'Column8', 'Column9', 'Column10']
    all_columns = ['Option1', 'Option2', 'Option3']

    ex = ScrollableWidget(df_columns, all_columns)
    ex.show()
    sys.exit(app.exec_())