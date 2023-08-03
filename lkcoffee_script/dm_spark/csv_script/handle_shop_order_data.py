
import pandas as pd
import numpy as np

file_path = '../data/shop_order_data.csv'
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
data_condition = (df["shop_dept_id"] == 326006) & (df["goods_id"] == 4488) & (df["dt"] == '2023-08-03')
query_data = df.loc[
    data_condition
]

print(type(query_data))
print(query_data['plan_finish_date'])
print(query_data['next_plan_finish_date'])

# 修改数据
# df.loc[
#     data_condition,
#     # 赋值的字段
#     'next_plan_finish_date'
# ] = '2023-08-10'

# 数据写入文件
# 不存储 index 信息: index=False
# df.to_csv(file_path, index=False)
