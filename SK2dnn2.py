import numpy as np
import pandas as pd
from keras import layers
import matplotlib.pyplot as plt
from keras.layers import Dropout
from keras.models import Sequential
from sklearn.metrics import mean_squared_error
from sklearn import preprocessing

# 生成训练数据集的函数
def create_dataset(X, Y, look_back=1):
    dataX, dataY = [], []
    for i in range(len(X) - look_back):
        dataX.append(X[i:(i + look_back)])
        dataY.append(Y[i + look_back])
    return np.array(dataX), np.array(dataY)


def mean_absolute_percentage_error(y_true, y_pred):
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


data = pd.read_csv('./dmq.csv')
X = data[data.columns[3:10]]  # 选取属性
Y = data[data.columns[10:15]]  # 选取标签数据

X = X.values
Y = Y.values

scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))  # 标准化范围
X = scaler.fit_transform(X)  # 对X进行标准化

trainNum = int(len(X) * 0.6)
valNum = int(len(X) * 0.8)

train_X = X[0:trainNum, :]
val_X = X[trainNum:valNum, :]
test_X = X[valNum:, :]

train_Y = Y[0:trainNum, :]
val_Y = Y[trainNum:valNum, :]
test_Y = Y[valNum:, :]

# 重塑输入数据
train_X = train_X.reshape((train_X.shape[0], train_X.shape[1]))
val_X = val_X.reshape((val_X.shape[0], val_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], test_X.shape[1]))

model = Sequential()
model.add(layers.Dense(16, activation='relu', input_shape=(train_X.shape[1],)))
model.add(Dropout(0.3))
model.add(layers.Dense(32, activation='relu'))
model.add(Dropout(0.3))
# model.add(layers.Dense(64, activation='relu'))
# model.add(Dropout(0.3))
# model.add(layers.Dense(32, activation='relu'))
# model.add(Dropout(0.3))
model.add(layers.Dense(16, activation='relu'))
model.add(Dropout(0.3))
model.add(layers.Dense(Y.shape[1]))

model.compile(loss='mean_squared_error', optimizer='adam')
model.summary()

hist = model.fit(train_X, train_Y, epochs=20, batch_size=64, validation_data=(val_X, val_Y))

loss = hist.history['loss']
val_loss = hist.history['val_loss']
print(loss)
print(val_loss)

trainScore = model.evaluate(train_X, train_Y, batch_size=32, verbose=0)
model.reset_states()
print('Train Score:', trainScore)

testScore = model.evaluate(test_X, test_Y, batch_size=32, verbose=0)
model.reset_states()
print('Test Score:', testScore)

valScore = model.evaluate(val_X, val_Y, batch_size=32, verbose=0)
model.reset_states()
print('Val Score:', valScore)

y_predict = model.predict(test_X, batch_size=16)
y_predict2 = model.predict(train_X, batch_size=16)
y_predict3 = model.predict(val_X, batch_size=16)

# 计算均方误差
mse = mean_squared_error(test_Y, y_predict)
# 计算均方根误差
rmse = np.sqrt(mse)
# 计算标准差
errors = test_Y - y_predict
std_deviation = np.std(errors)

print(f"均方根误差 ± 标准差: {rmse:.3f} ± {std_deviation:.2f}")

# 计算MAPE
mape = mean_absolute_percentage_error(test_Y, y_predict)
print(f"平均绝对百分比误差 (MAPE): {mape:.2f}%")

# 绘制图像
plt.figure(figsize=(8, 6))
plt.imshow(test_X, cmap='viridis', extent=[0, 1, 0, 1], origin='lower')
plt.colorbar(label='电阻率 (Ω·m)')
plt.xlabel('X轴')
plt.show()

# # 绘制损失曲线
# fig, loss_ax = plt.subplots(figsize=(10, 8), dpi=150)
# loss_ax.plot(loss, 'y', label='train loss')
# loss_ax.plot(val_loss, 'r', label='val loss')
# loss_ax.set_xlabel('epoch')
# loss_ax.set_ylabel('loss')
# loss_ax.legend(loc='upper left')
# plt.show()
#
# # 绘制预测与实际值对比图
# plt.figure(figsize=(10,8),dpi=150)
# i=1
# for group in range(test_Y.shape[1]):
#     plt.subplot(test_Y.shape[1],1,i);
#     plt.plot(test_Y[:,group],color='red',label='Original', linewidth=1)
#     # plt.plot(y_predict[:,0],color='green',label='Predict')
#     plt.plot(y_predict[:,group],color='green',label='Predict', linewidth=1)
#     plt.xlabel('the number of test data')
#     plt.ylabel('Soil moisture')
#     plt.legend()
#     i=i+1
# plt.show()
#
#
#
# plt.figure(figsize=(10,8),dpi=150)
# i=1
# for group in range(train_Y.shape[1]):
#     plt.subplot(train_Y.shape[1],1,i);
#     plt.plot(train_Y[:,group],color='red',label='Original', linewidth=1)
#     # plt.plot(y_predict[:,0],color='green',label='Predict')
#     plt.plot(y_predict2[:,group],color='green',label='Predict', linewidth=1)
#     plt.xlabel('the number of train data')
#     plt.ylabel('Soil moisture')
#     plt.legend()
#     i=i+1
# plt.show()
#
#
# plt.figure(figsize=(10,8),dpi=150)
# i=1
# for group in range(val_Y.shape[1]):
#     plt.subplot(val_Y.shape[1],1,i);
#     plt.plot(val_Y[:,group],color='red',label='Original', linewidth=1)
#     # plt.plot(y_predict[:,0],color='green',label='Predict')
#     plt.plot(y_predict3[:,group],color='green',label='Predict', linewidth=1)
#     plt.xlabel('the number of val data')
#     plt.ylabel('Soil moisture')
#     plt.legend()
#     i=i+1
# plt.show()