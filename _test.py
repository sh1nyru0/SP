import os
import pandas as pd

# 读取从 Shapefile 导出的 CSV 文件
shapefile_data = pd.read_csv("path_to_exported_csv.csv")

# 基本目录路径（根据需要调整）
output_base_dir = "recovered_project_directory"

# 遍历每条记录，根据 directory 和 filename 还原目录结构
for _, row in shapefile_data.iterrows():
    directory = row['directory']
    filename = row['filename']

    # 创建输出目录路径
    output_dir = os.path.join(output_base_dir, directory)
    os.makedirs(output_dir, exist_ok=True)

    # 创建 CSV 文件路径
    output_file = os.path.join(output_dir, filename)

    # 将每条记录保存到相应的文件中
    # 注意：这是一个简单示例，实际保存时要处理多个记录保存到同一文件的问题
    # 可以基于 filename 分组数据并批量保存
    with open(output_file, 'a') as f:
        f.write(','.join(map(str, row.values)) + '\n')

print("目录结构已还原!")
