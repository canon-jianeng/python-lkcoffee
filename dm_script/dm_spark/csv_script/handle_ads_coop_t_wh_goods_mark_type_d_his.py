
import pandas as pd
import numpy as np

file_path = '../data/ads_coop_t_wh_goods_mark_type_d_his.csv'
# 选择不读取第一列: index_col=0
df = pd.read_csv(file_path)

# 显示所有列
# pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)

# 查看全部的列字段
columns = df.columns
print(columns)

# 查询条件
# 测试数据日期: 2024-01-22
data_condition = (df["dt"] == '2024-01-22')
# data_condition = (df["dt"] == '2024-01-22') & (df["mark_type"] == 2)
# data_condition = (df["goods_id"] == 370) & (df["dt"] == '2024-01-22')
query_data = df.loc[
    data_condition
]

# print(query_data)
# print(type(mark_type))
print(query_data['goods_id'])
# print(query_data['mark_type'])

# 修改数据
# df.loc[
#     data_condition,
#     # 赋值的字段
#     'mark_type'
# ] = '2'

# 数据写入文件
# 不存储 index 信息: index=False
# df.to_csv(file_path, index=False)
