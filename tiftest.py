import numpy as np
import os
from PIL import Image
from osgeo import gdal

# Stop GDAL printing both warnings and errors to STDERR
gdal.PushErrorHandler('CPLQuietErrorHandler')

# Make GDAL raise python exceptions for errors (warnings won't raise an exception)
gdal.UseExceptions()


def readTif(imgPath, bandsOrder=[3, 2, 1]):
    """
    读取GEO tif影像的前三个波段值，并按照R.G.B顺序存储到形状为【原长*原宽*3】的数组中
    :param imgPath: 图像存储全路径
    :param bandsOrder: RGB对应的波段顺序，如高分二号多光谱包含蓝，绿，红，近红外四个波段，RGB对应的波段为3，2，1
    :return: R.G.B三维数组
    """
    dataset = gdal.Open(imgPath, gdal.GA_ReadOnly)  # 返回一个gdal.Dataset类型的对象
    cols = dataset.RasterXSize  # tif图像的宽度
    rows = dataset.RasterYSize  # tif图像的高度
    data = np.empty([rows, cols, 3], dtype=float)  # 定义结果数组，将RGB三波段的矩阵存储
    for i in range(3):
        band = dataset.GetRasterBand(bandsOrder[i])  # 读取波段数值
        oneband_data = band.ReadAsArray()  # 读取波段数值读为numpy数组
        # print(oneband_data)
        data[:, :, i] = oneband_data  # 将读取的结果存放在三维数组的一页三
    return data


def stretchImg(imgPath, resultPath, lower_percent=0.5, higher_percent=99.5):
    """
    #将光谱DN值映射至0-255，并保存
    :param imgPath: 需要转换的tif影像路径（***.tif）
    :param resultPath: 转换后的文件存储路径(***.jpg)
    :param lower_percent: 低值拉伸比率
    :param higher_percent: 高值拉伸比率
    :return: 无返回参数，直接输出图片
    """
    print(imgPath)
    RGB_Array = readTif(imgPath)
    print(RGB_Array.shape)
    band_Num = RGB_Array.shape[2]  # 数组第三维度的大小，在这里是图像的通道数
    JPG_Array = np.zeros_like(RGB_Array, dtype=np.uint8)
    for i in range(band_Num):
        minValue = 0
        maxValue = 255
        # 获取数组RGB_Array某个百分比分位上的值
        low_value = np.percentile(RGB_Array[:, :, i], lower_percent)
        high_value = np.percentile(RGB_Array[:, :, i], higher_percent)
        temp_value = minValue + (RGB_Array[:, :, i] - low_value) * (maxValue - minValue) / (high_value - low_value)
        temp_value[temp_value < minValue] = minValue
        temp_value[temp_value > maxValue] = maxValue
        JPG_Array[:, :, i] = temp_value
    outputImg = Image.fromarray(np.uint8(JPG_Array))
    outputImg.save(resultPath)


def Batch_Convert_tif_to_jpg(imgdir, savedir):
    # 获取文件夹下所有tif文件名称，并存入列表
    file_name_list = os.listdir(imgdir)
    for name in file_name_list:
        # 获取图片文件全路径
        img_path = os.path.join(imgdir, name)
        # 获取文件名，不包含扩展名
        filename = os.path.splitext(name)[0]
        print(filename)
        savefilename = filename + "_no" + ".jpg"
        # 文件存储全路径
        savepath = os.path.join(savedir, savefilename)
        # img_path为tif文件的完全路径
        # savepath为tif文件对应的jpg文件的完全路径
        print(savepath)
        stretchImg(img_path, savepath)
        print("图片:【", filename, "】完成转换")
    print("完成所有图片转换!")


if __name__ == '__main__':
    imgdir = r"D:\SP\tif"  # tif文件所在的【文件夹】
    savedir = r"D:\SP\output"  # 转为jpg后存储的【文件夹】
    Batch_Convert_tif_to_jpg(imgdir, savedir)

