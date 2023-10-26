
import pandas as pd
import numpy as np

file_path = '../data/dinghuo_target_inventory_week.csv'
df = pd.read_csv(file_path)

# 显示所有列
# pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)

# 查看全部的列字段
columns = df.columns
print(columns)

# 查询条件
data_condition = (df["predict_date"] == '2023-10-19')
# data_condition = (df["predict_date"] == '2023-10-24') & (df["goods_id"] == 25694)
# data_condition = (df["goods_id"] == 25694)
query_data = df.loc[
    data_condition
]

# print(type(query_data))
# print(query_data)
print(query_data['predict_date'])
# print(query_data['pred_consume'])


# 一、删除，查询部分数据(过滤不需要的数据)
# df.loc[
#     data_condition
# ].to_csv(file_path, index=False)


# 二、修改数据
# df.loc[
#     data_condition,
#     # 赋值的字段
#     'predict_date'
# ] = '2023-10-19'

# 数据写入文件
# 不存储 index 信息: index=False
# df.to_csv(file_path, index=False)
