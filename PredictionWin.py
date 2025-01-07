import os
import sys

import numpy as np
import pandas as pd
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFileDialog
from matplotlib import pyplot as plt
from qtpy import uic
from keras.models import load_model
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler


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
class PredictionWin:
    def __init__(self, path):
        self.ui = uic.loadUi("prediction.ui")
        self.ui.btnModel.clicked.connect(self.chooseModel)
        self.ui.btnData.clicked.connect(self.chooseData)
        self.ui.btnok.clicked.connect(self.ok)
        self.path = path
        self.dataPath = None
        self.modelPath = None

        # 重定向标准输出到 QPlainTextEdit
        sys.stdout = StreamToQPlainTextEdit(self.ui.log)
        self.model = None

    def chooseData(self):
        self.dataPath,_ = QFileDialog.getOpenFileName(
            self.ui,
            "选择数据",
            "",
            "文件类型(*.csv)"
        )
        self.ui.dataEdit.setText(os.path.basename(self.dataPath))
        self.ui.dataEdit.setReadOnly(True)

    def chooseModel(self):
        self.modelPath,_ = QFileDialog.getOpenFileName(
            self.ui,
            "选择模型",
            self.path + "/模型",
            "文件类型(*.h5)"
        )
        self.ui.modelEdit.setText(os.path.basename(self.modelPath))
        self.ui.modelEdit.setReadOnly(True)

    def mean_absolute_percentage_error(self, y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def ok(self):
        data = pd.read_csv(self.dataPath)
        X = data.iloc[:, int(self.ui.attributel.text()): int(self.ui.attributer.text())]
        Y = data.iloc[:, int(self.ui.tagl.text()): int(self.ui.tagr.text())]
        model = load_model(self.modelPath)

        X = X.to_numpy()
        Y = Y.to_numpy()

        # 数据预处理
        scaler = MinMaxScaler(feature_range=(0, 1))
        X = scaler.fit_transform(X)

        # 划分数据集
        totol = self.ui.train.value() + self.ui.check.value() + self.ui.test.value()
        trainNum = int(len(X) * (self.ui.train.value() / totol))
        valNum = int(len(X) * ((self.ui.train.value() + self.ui.check.value()) / totol))

        train_X = X[0:trainNum, :]
        val_X = X[trainNum:valNum, :]
        test_X = X[valNum:, :]

        train_Y = Y[0:trainNum, :]
        val_Y = Y[trainNum:valNum, :]
        test_Y = Y[valNum:, :]

        # 使用模型进行预测
        y_predict_train = model.predict(train_X)
        y_predict_val = model.predict(val_X)
        y_predict_test = model.predict(test_X)

        # 重新评估模型以获取损失值
        train_loss = model.evaluate(train_X, train_Y, batch_size=32, verbose=0)
        val_loss = model.evaluate(val_X, val_Y, batch_size=32, verbose=0)
        test_loss = model.evaluate(test_X, test_Y, batch_size=32, verbose=0)

        print(f"Train Loss: {train_loss}")
        print(f"Validation Loss: {val_loss}")
        print(f"Test Loss: {test_loss}")

        hist = model.fit(train_X, train_Y, epochs=20, batch_size=64, validation_data=(val_X, val_Y))

        # 绘制训练损失和验证损失
        loss = model.history.history['loss']
        val_loss = model.history.history['val_loss']

        plt.figure(figsize=(10, 8), dpi=150)
        plt.plot(loss, 'y', label='Train Loss')
        plt.plot(val_loss, 'r', label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(loc='upper left')
        plt.title('Training and Validation Loss')
        plt.show()

        # 计算MAPE
        mape = mean_absolute_percentage_error(test_Y, y_predict_test)
        print(f"平均绝对百分比误差 (MAPE): {mape:.2f}%")

        # 计算mse
        mse_test = mean_squared_error(test_Y, y_predict_test)
        print(f"测试集的均方根误差为: {mse_test:.2f}")

        # 绘制测试集预测结果
        plt.figure(figsize=(10, 8), dpi=150)
        for group in range(test_Y.shape[1]):
            plt.subplot(test_Y.shape[1], 1, group + 1)
            plt.plot(test_Y[:, group], color='red', linewidth=1, label='True')
            plt.plot(y_predict_test[:, group], color='green', linewidth=1, label='Predicted')
            plt.xlabel('Number of Test Data Points')
            plt.ylabel('Value')
            plt.legend()
        plt.suptitle('Test Set Predictions vs True Values')
        plt.tight_layout()
        plt.show()

        # 绘制训练集预测结果
        plt.figure(figsize=(10, 8), dpi=150)
        for group in range(train_Y.shape[1]):
            plt.subplot(train_Y.shape[1], 1, group + 1)
            plt.plot(train_Y[:, group], color='red', linewidth=1, label='True')
            plt.plot(y_predict_train[:, group], color='green', linewidth=1, label='Predicted')
            plt.xlabel('Number of Train Data Points')
            plt.ylabel('Value')
            plt.legend()
        plt.suptitle('Train Set Predictions vs True Values')
        plt.tight_layout()
        plt.show()

        # 绘制验证集预测结果
        plt.figure(figsize=(10, 8), dpi=150)
        for group in range(val_Y.shape[1]):
            plt.subplot(val_Y.shape[1], 1, group + 1)
            plt.plot(val_Y[:, group], color='red', linewidth=1, label='True')
            plt.plot(y_predict_val[:, group], color='green', linewidth=1, label='Predicted')
            plt.xlabel('Number of Validation Data Points')
            plt.ylabel('Value')
            plt.legend()
        plt.suptitle('Validation Set Predictions vs True Values')
        plt.tight_layout()
        plt.show()

    def cancel(self):
        self.ui.close()