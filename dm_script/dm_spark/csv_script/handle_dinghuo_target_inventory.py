
import pandas as pd
import numpy as np

file_path = '../data/dinghuo_target_inventory.csv'
df = pd.read_csv(file_path)

# 显示所有列
# pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)

# 查看全部的列字段
columns = df.columns
print(columns)

# 查询条件
# data_condition = (df["dt"] == '2023-10-25')
data_condition = (df["predict_date"] == '2023-12-12')
# data_condition = (df["predict_date"] == '2023-12-12') & (df["goods_id"] == 25533)
# data_condition = (df["goods_id"] == 27178)
query_data = df.loc[
    data_condition
]

# print(type(query_data))
# print(query_data)
# print(query_data['predict_date'])
# print(query_data['pred_consume'])

# 根据 dt 查询 predict_date 的日期
df_data = pd.DataFrame(query_data['goods_id'])
# 根据所有列删除重复的行, 默认保留第一次出现的重复值
# 删除特定列上的重复项
df_data = df_data.drop_duplicates(subset=['goods_id'])
print(df_data)

# 一、删除，查询部分数据(过滤不需要的数据)
# df.loc[
#     data_condition
# ].to_csv(file_path, index=False)


# 二、修改数据
# df.loc[
#     data_condition,
#     # 赋值的字段
#     'goods_id'
# ] = '6967'

# 数据写入文件
# 不存储 index 信息: index=False
# df.to_csv(file_path, index=False)
