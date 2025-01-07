import sys
import numpy as np
import pandas as pd
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFileDialog
from keras import Sequential
from keras.losses import mean_absolute_percentage_error
from matplotlib import pyplot as plt
from pyqtgraph import QtWidgets
from qtpy import uic
from sklearn import preprocessing
from keras import layers
from sklearn.metrics import mean_squared_error

class StreamToQPlainTextEdit:
    """将标准输出重定向到 QPlainTextEdit 的类"""
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, message):
        # 将消息追加到 QPlainTextEdit
        self.text_edit.appendPlainText(message.strip())
        self.text_edit.ensureCursorVisible()  # 自动滚动到底部
        QCoreApplication.processEvents()

    def flush(self):
        """为兼容性，flush 是必须的空实现"""
        pass

class LstmWin:
    def __init__(self, path):
        self.ui = uic.loadUi("lstm.ui")
        self.ui.btnok.clicked.connect(self.ok)
        self.ui.btncancel.clicked.connect(self.cancel)
        self.ui.chooseFile.clicked.connect(self.chooseFile)
        self.ui.log.setReadOnly(True)
        self.ui.save.clicked.connect(self.onSave)
        if not self.ui.container.layout():
            self.ui.container.setLayout(QtWidgets.QVBoxLayout())
        self.ui.btnlevel.clicked.connect(self.onLevel)
        self.levelNum = 0
        self.arr1 = []
        self.arr2 = []
        self.filePath = None
        self.path = path
        # 重定向标准输出到 QPlainTextEdit
        sys.stdout = StreamToQPlainTextEdit(self.ui.log)
        self.model = None

    def onLevel(self):
        try:
            levelNum = int(self.ui.level.text())
            self.levelNum = levelNum
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "错误", "请输入有效的数字")
            return

        for i in reversed(range(self.ui.container.layout().count())):
            self.arr1 = []
            self.arr2 = []
            widget = self.ui.container.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for i in range(levelNum):
            hlayout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"第{i + 1}层：")
            hlayout.addWidget(label)

            label1 = QtWidgets.QLabel("神经元个数：")
            text_edit1 = QtWidgets.QTextEdit()
            self.arr1.append(text_edit1)
            text_edit1.setFixedHeight(label1.sizeHint().height())  # 将高度设置为和 label 相同
            label2 = QtWidgets.QLabel("Dropout率：")
            text_edit2 = QtWidgets.QTextEdit()
            self.arr2.append(text_edit2)
            text_edit2.setFixedHeight(label2.sizeHint().height())  # 将高度设置为和 label 相同
            hlayout.addWidget(label1)
            hlayout.addWidget(text_edit1)
            hlayout.addWidget(label2)
            hlayout.addWidget(text_edit2)

            # 使用拉伸因子使控件均匀占满整行
            hlayout.setStretch(0, 1)  # "第i层" 标签的拉伸因子
            hlayout.setStretch(1, 1)  # "神经元个数" 标签的拉伸因子
            hlayout.setStretch(2, 2)  # 神经元个数输入框的拉伸因子
            hlayout.setStretch(3, 1)  # "Dropout率" 标签的拉伸因子
            hlayout.setStretch(4, 2)  # Dropout率输入框的拉伸因子

            levelWidget = QtWidgets.QWidget()
            levelWidget.setLayout(hlayout)

            self.ui.container.layout().addWidget(levelWidget)



    def onSave(self):
        model_all = self.path + "/模型/" + self.ui.name.text() + ".h5"
        self.model.save(model_all)
        print(f"{self.ui.name.text()}模型已保存")

    def chooseFile(self):
        self.filePath,_ = QFileDialog.getOpenFileName(
            self.ui,
            "选择输入的数据集",
            "",
            "文件类型(*.csv)",
        )

    # 生成训练数据集的函数
    def create_dataset(self, X, Y, look_back=1):
        dataX, dataY = [], []
        for i in range(len(X) - look_back):
            dataX.append(X[i:(i + look_back), :])
            dataY.append(Y[i + look_back, :])
        return np.array(dataX), np.array(dataY)


    def mean_absolute_percentage_error(self ,y_true, y_pred):
        """
        Calculate the Mean Absolute Percentage Error (MAPE).

        Parameters:
        y_true (array-like): The ground truth values.
        y_pred (array-like): The predicted values.

        Returns:
        float: The MAPE value.
        """
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def ok(self):
        data = pd.read_csv(self.filePath)
        # X = data[data.columns[3:10]]  # 选取属性
        X = data[data.columns[self.ui.attributel.value():self.ui.attributer.value()]]  # 选取属性

        Y = data[data.columns[self.ui.tagl.value():self.ui.tagr.value()]]  # 选取标签数据
        # Y = data[data.columns[yarray]]  # 选取标签数据

        X = X.values
        Y = Y.values

        scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))  # 标准化范围
        X = scaler.fit_transform(X)  # 对X进行标准化

        totol = self.ui.train.value() + self.ui.check.value() + self.ui.test.value()

        trainNum = int(len(X) * (self.ui.train.value()/totol))
        # trainNum = int(len(X) * num)
        valNum = int(len(X) * ((self.ui.train.value() + self.ui.check.value()) / totol))

        train_X = X[0:trainNum, :]
        val_X = X[trainNum:valNum, :]
        test_X = X[valNum:, :]

        train_Y = Y[0:trainNum, :]
        val_Y = Y[trainNum:valNum, :]
        test_Y = Y[valNum:, :]

        look_back = int(self.ui.lookback.text())
        # look_back = 100步长
        train_X, train_Y = self.create_dataset(train_X, train_Y, look_back)
        val_X, val_Y = self.create_dataset(val_X, val_Y, look_back)
        test_X, test_Y = self.create_dataset(test_X, test_Y, look_back)

        print("Validation set shape:", val_X.shape)
        # self.log(f"Validation set shape: {val_X.shape}")

        train_X = np.reshape(train_X, (train_X.shape[0], train_X.shape[1], train_X.shape[2]))
        val_X = np.reshape(val_X, (val_X.shape[0], val_X.shape[1], val_X.shape[2]))
        test_X = np.reshape(test_X, (test_X.shape[0], test_X.shape[1], test_X.shape[2]))

        model = Sequential()
        for i in range(self.levelNum - 1):
            if i == 0:
                model.add(layers.LSTM(int(self.arr1[i].toPlainText()), return_sequences=True, input_shape=(look_back, train_X.shape[2])))
                model.add(layers.Dropout(int(self.arr2[i].toPlainText())))
            else:
                model.add(layers.LSTM(int(self.arr1[i].toPlainText()), return_sequences=True))
                model.add(layers.Dropout(int(self.arr2[i].toPlainText())))
            if i == self.levelNum - 2:
                model.add(layers.LSTM(int(self.arr1[i].toPlainText()), return_sequences=False))
                model.add(layers.Dropout(int(self.arr2[i].toPlainText())))

        model.add(layers.Dense(int(self.arr1[self.levelNum - 1].toPalinText())))
        model.add(layers.Dropout(int(self.arr2[self.levelNum -1].toPlainText())))

        #
        # model.add(layers.LSTM(8, return_sequences=True, input_shape=(look_back, train_X.shape[2])))
        # model.add(layers.Dropout(0.3))
        # # model.add(layers.LSTM(16, return_sequences=True))
        # # model.add(layers.Dropout(0.3))
        # # model.add(layers.LSTM(32, return_sequences=True))
        # # model.add(layers.Dropout(0.3))
        # model.add(layers.LSTM(16, return_sequences=False))
        # model.add(layers.Dropout(0.3))
        #
        # model.add(layers.Dense(8))
        model.add(layers.Dense(Y.shape[1]))

        model.compile(loss='mean_squared_error', optimizer='adam')
        model.summary()

        hist = model.fit(train_X, train_Y, epochs=20, batch_size=64, validation_data=(val_X, val_Y))

        loss = hist.history['loss']
        val_loss = hist.history['val_loss']
        print(loss)
        # self.log(f"Training loss: {hist.history['loss']}")
        print(val_loss)
        # self.log(f"Validation loss: {hist.history['val_loss']}")

        trainScore = model.evaluate(train_X, train_Y, batch_size=64, verbose=0)
        model.reset_states()
        print('Train Score:', trainScore)
        # self.log(f'Train Score: {trainScore}')

        testScore = model.evaluate(test_X, test_Y, batch_size=64, verbose=0)
        model.reset_states()
        print('Test Score:', testScore)
        # self.log(f'Test Score: {testScore}')

        valScore = model.evaluate(val_X, val_Y, batch_size=64, verbose=0)
        model.reset_states()
        print('Val Score:', valScore)
        # self.log(f'Val Score: {valScore}')

        y_predict = model.predict(test_X, batch_size=64)
        y_predict2 = model.predict(train_X, batch_size=64)
        y_predict3 = model.predict(val_X, batch_size=64)

        self.model = model

        # 计算均方误差
        mse = mean_squared_error(test_Y, y_predict)
        # 计算均方根误差
        rmse = np.sqrt(mse)
        # 计算标准差
        errors = test_Y - y_predict
        std_deviation = np.std(errors)

        print(f"均方根误差 ± 标准差: {rmse:.3f} ± {std_deviation:.2f}")
        # self.log(f"均方根误差 ± 标准差: {rmse:.3f} ± {std_deviation:.2f}")

        # 计算MAPE
        mape = mean_absolute_percentage_error(test_Y, y_predict)
        # print(f"平均绝对百分比误差 (MAPE): {mape:.2f}%")
        # print(f"平均绝对百分比误差 (MAPE): {mape}%")

        fig, loss_ax = plt.subplots(figsize=(10, 8), dpi=150)
        loss_ax.plot(loss, 'y', label='train loss')
        loss_ax.plot(val_loss, 'r', label='val loss')
        loss_ax.set_xlabel('epoch')
        loss_ax.set_ylabel('loss')
        loss_ax.legend(loc='upper left')
        plt.show()

        plt.figure(figsize=(10, 8), dpi=150)
        i = 1
        for group in range(test_Y.shape[1]):
            plt.subplot(test_Y.shape[1], 1, i)
            plt.plot(test_Y[:, group], color='red', linewidth=1)
            # plt.plot(y_predict[:,0],color='green',label='Predict')
            plt.plot(y_predict[:, group], color='green', linewidth=1)
            plt.xlabel('the number of test data')
            plt.ylabel('Soil moisture')
            # plt.legend()
            i = i + 1
        plt.show()

        plt.figure(figsize=(10, 8), dpi=150)
        i = 1
        for group in range(train_Y.shape[1]):
            plt.subplot(train_Y.shape[1], 1, i)
            plt.plot(train_Y[:, group], color='red', linewidth=1)
            # plt.plot(y_predict[:,0],color='green',label='Predict')
            plt.plot(y_predict2[:, group], color='green', linewidth=1)
            plt.xlabel('the number of train data')
            plt.ylabel('Soil moisture')
            # plt.legend()
            i = i + 1
        plt.show()

        plt.figure(figsize=(10, 8), dpi=150)
        i = 1
        for group in range(val_Y.shape[1]):
            plt.subplot(val_Y.shape[1], 1, i)
            plt.plot(val_Y[:, group], color='red', linewidth=1)
            # plt.plot(y_predict[:,0],color='green',label='Predict')
            plt.plot(y_predict3[:, group], color='green', linewidth=1)
            plt.xlabel('the number of val data')
            plt.ylabel('Soil moisture')
            # plt.legend()
            i = i + 1
        plt.show()

    def cancel(self):
        self.ui.close()