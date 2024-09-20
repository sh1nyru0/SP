import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 定义 CSV 文件所在的基路径
base_dir = "D:/SP/project/test"  # 替换为你的项目路径
directories = ["重力文件", "磁法文件", "电法文件"]  # 不同数据文件的目录名称

# 初始化空的 GeoDataFrame，用于存储合并后的数据
combined_gdf = gpd.GeoDataFrame()

# 固定点作为几何信息，例如使用 (0, 0) 作为所有记录的点
default_geometry = Point(0, 0)

# 遍历每个子目录
for directory in directories:
    dir_path = os.path.join(base_dir, directory)

    # 遍历子目录中的每个 CSV 文件
    for filename in os.listdir(dir_path):
        if filename.endswith(".csv"):
            csv_path = os.path.join(dir_path, filename)

            # 读取 CSV 文件
            df = pd.read_csv(csv_path)

            # 创建几何列，所有点固定为 (0, 0)
            df['geometry'] = default_geometry

            # 将 pandas DataFrame 转为 GeoDataFrame
            gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")  # 使用 WGS84 投影 (EPSG:4326)

            # 在每个文件的数据中增加列，标识来源文件夹和文件名
            gdf['directory'] = directory  # 标识数据来源的目录
            gdf['filename'] = filename  # 标识数据来源的文件

            # 将当前文件的 GeoDataFrame 追加到合并的 GeoDataFrame 中
            combined_gdf = pd.concat([combined_gdf, gdf], ignore_index=True)

# 保存合并后的 Shapefile
output_shapefile = os.path.join(base_dir, "combined_data.shp")
combined_gdf.to_file(output_shapefile)

print(f"Combined Shapefile saved: {output_shapefile}")
