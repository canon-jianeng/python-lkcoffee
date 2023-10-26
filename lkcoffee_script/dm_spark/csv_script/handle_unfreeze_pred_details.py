
import pandas as pd
import numpy as np

file_path = '../data/unfreeze_pred_details_yesterday.csv'
df = pd.read_csv(file_path)

# 显示所有列
# pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)

# 查看全部的列字段
columns = df.columns
print(columns)

# 查询条件
data_condition = (df["goods_id"] == 28029)
query_data = df.loc[
    data_condition
]

# print(type(query_data))
# print(query_data)
print(query_data['pred_consume'])


# 修改数据
# df.loc[
#     data_condition,
#     # 赋值的字段
#     'pred_consume'
# ] = 0

# 数据写入文件
# 不存储 index 信息: index=False
# df.to_csv(file_path, index=False)
