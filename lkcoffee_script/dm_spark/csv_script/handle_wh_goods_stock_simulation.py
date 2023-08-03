
import pandas as pd
import numpy as np

file_path = "../data/wh_goods_stock_simulation.csv"
df = pd.read_csv(file_path)

# 显示所有列
# pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)

# 显示前5行
# print(df["wh_dept_id"][:5])

# 查看全部的列字段
columns = df.columns
print(columns)

# 查询条件
data_condition = (df["wh_dept_id"] == 4001) & (df["goods_id"] == 24) & (df["use_day"] > 0)
query_data = df.loc[
    # 查询条件
    data_condition
]

test_data = df.loc[
    # 查询条件
    data_condition,
    # 字段
    'use_day'
]

# 查找 test_data 全部对应的行
isin_data = df[df['use_day'].isin(test_data)]

print(query_data)

# 修改数据
# df.loc[
#     # 查询条件
#     data_condition,
#     # 赋值的字段
#     'use_day'
# ] = 3

# 数据写入文件
# 不存储 index 信息: index=False
# df.to_csv(file_path, index=False)
