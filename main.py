from libs.share import SI
from PyQt5.QtWidgets import QApplication          
from win_main import Win_Start

app = QApplication([])
SI.startWin = Win_Start()
SI.startWin.ui.show()
app.exec()