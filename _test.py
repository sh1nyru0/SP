from PyQt5 import QtWidgets, QtCore
import sys

class Win_Filter(QtWidgets.QWidget):
    # 定义一个信号，信号携带一个字符串信息
    closed_signal = QtCore.pyqtSignal(str)

    def __init__(self, filePath, title):
        super().__init__()
        self.setWindowTitle(title)
        self.filePath = filePath

    # 重写 closeEvent，捕捉窗口关闭事件
    def closeEvent(self, event):
        # 在窗口关闭时发射信号，传递信息
        self.closed_signal.emit(f"窗口关闭，传递的信息：{self.filePath}")
        event.accept()

# 外部函数，用于接收信号传递的内容
def handle_closed(info):
    print(f"外部接收到信号，传递的信息: {info}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # 创建窗口对象
    SI = type('', (), {})()  # 创建一个临时的对象用来存储 window
    SI.filterWin = Win_Filter("文件路径", "窗口标题")

    # 连接自定义信号到外部处理函数
    SI.filterWin.closed_signal.connect(handle_closed)

    # 显示窗口
    SI.filterWin.show()

    # 程序主循环
    sys.exit(app.exec_())

