import sys
import random
import numpy as np
import pandas as pd
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFileDialog
from matplotlib import pyplot as plt
from qtpy import uic
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


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


class KmeansWin:
    def __init__(self, path):
        self.ui = uic.loadUi("kmeans.ui")
        self.ui.btnok.clicked.connect(self.ok)
        self.ui.btncancel.clicked.connect(self.cancel)
        self.ui.btnk.clicked.connect(self.elbow)
        self.ui.chooseFile.clicked.connect(self.chooseFile)
        self.ui.log.setReadOnly(True)
        sys.stdout = StreamToQPlainTextEdit(self.ui.log)

        self.filePath = None
        # 重定向标准输出到 QPlainTextEdit
        sys.stdout = StreamToQPlainTextEdit(self.ui.log)

    def elbow(self):
        df = pd.read_csv(self.filePath)
        data = df.iloc[:, [self.ui.x.value(), self.ui.y.value(), self.ui.z.value()]]
        # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(data)

        # 使用肘部法则确定最佳的K值
        wcss = []  # Within Cluster Sum of Squares
        for i in range(1, 21):
            kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
            kmeans.fit(X_scaled)
            wcss.append(kmeans.inertia_)

        plt.figure(figsize=(10, 5))
        plt.plot(range(1, 21), wcss, marker='o', linestyle='--')
        plt.title('Elbow Method')
        plt.xlabel('Number of clusters')
        plt.ylabel('WCSS')
        plt.show()


    # K-means++ 初始化
    def kmeans_plus_plus(self ,dataSet, k):
        centroids = [random.choice(dataSet)]
        for _ in range(1, k):
            dists = np.min(self.calcDis(dataSet, centroids, len(centroids)), axis=1)
            probs = dists / np.sum(dists)
            cumulative_probs = np.cumsum(probs)
            r = random.random()
            index = np.searchsorted(cumulative_probs, r)
            centroids.append(dataSet[index])
        return np.array(centroids)

    # 使用k-means分类
    def kmeans(self, dataSet, weights, k, tol, plus):
        if plus:
            # 使用K-means_plus_plus
            centroids = self.kmeans_plus_plus(dataSet, k)

        else:
            # 随机取质心
            centroids = random.sample(dataSet, k)

        # 更新质心 直到变化量小于阈值
        changed, newCentroids = self.classify(dataSet, weights, centroids, k)
        while np.any(np.linalg.norm(changed, axis=1) > tol):
            prev_centroids = newCentroids.copy()
            changed, newCentroids = self.classify(dataSet, weights, newCentroids, k)
            changed = newCentroids - prev_centroids

        centroids = newCentroids  # 不再排序，以保持质心的对应关系

        # 根据质心计算每个集群
        cluster = []
        clalist = self.calcDis(dataSet, centroids, k)  # 调用欧拉距离
        minDistIndices = np.argmin(clalist, axis=1)
        for i in range(k):
            cluster.append([])
        for i, j in enumerate(minDistIndices):  # enymerate()可同时遍历索引和遍历元素
            cluster[j].append(dataSet[i])

        return centroids, cluster

    # 创建权重
    def createWeights(self, dataSet, weight):
        return [weight] * len(dataSet)  # 默认权重为1，可以根据需要调整

    def ok(self):
        df = pd.read_csv(self.filePath)
        data = df.iloc[:, [self.ui.x.value(), self.ui.y.value(), self.ui.z.value()]]
        data = data.values.tolist()
        weights = self.createWeights(data, self.ui.sbweights.value())
        centroids, cluster = self.kmeans(data, weights, self.ui.sbk.value(), float(self.ui.le.text()), self.ui.cb.isChecked())
        print('质心为：%s' % centroids)
        print('集群为：%s' % cluster)
        # 绘制原始点
        for i in range(len(data)):
            plt.scatter(data[i][0], data[i][1], marker='o', color='green', s=40, label='原始点' if i == 0 else "")
        # 绘制质心
        for j in range(len(centroids)):
            plt.scatter(centroids[j][0], centroids[j][1], marker='x', color='red', s=50, label='质心' if i == 0 else "")
        plt.legend()
        plt.show()


    # 计算欧拉距离
    def calcDis(self ,dataSet, centroids, k):
        clalist = []
        for data in dataSet:
            diff = np.tile(data, (k, 1)) - centroids
            squaredDiff = diff ** 2  # 平方
            squaredDist = np.sum(squaredDiff, axis=1)  # 和(axis=1表示行)
            distance = squaredDist ** 0.5  # 开根号
            clalist.append(distance)
        clalist = np.array(clalist)  # 返回一个每个点到质点的距离len(dateSet)*k的数组
        return clalist

    def chooseFile(self):
        self.filePath,_ = QFileDialog.getOpenFileName(
            self.ui,
            "选择输入的数据集",
            "",
            "文件类型(*.csv)",
        )

    def weighted_mean(self, data, weights):
        return np.average(data, axis=0, weights=weights)

    # 计算质心
    def classify(self ,dataSet, weights, centroids, k):
        # 计算样本到质心的距离
        clalist = self.calcDis(dataSet, centroids, k)
        # 分组并计算新的质心
        minDistIndices = np.argmin(clalist, axis=1)
        newCentroids = []
        for i in range(k):
            cluster_points = np.array([dataSet[j] for j in range(len(dataSet)) if minDistIndices[j] == i])
            cluster_weights = np.array(
                [weights[j] for j in range(len(dataSet)) if minDistIndices[j] == i])  # 默认权重为1，可以根据需要调整
            if len(cluster_points) > 0:
                newCentroids.append(self.weighted_mean(cluster_points, cluster_weights))
            else:
                newCentroids.append(centroids[i])  # 如果簇为空，保持原质心
        newCentroids = np.array(newCentroids)
        changed = newCentroids - centroids
        return changed, newCentroids


    def cancel(self):
        self.ui.close()