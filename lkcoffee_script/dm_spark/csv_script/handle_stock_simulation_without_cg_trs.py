
import pandas as pd
import numpy as np

file_path = '../data/part-0.csv'
# 选择不读取第一列: index_col=0
df = pd.read_csv(file_path)

# 显示所有列
# pd.set_option('display.max_columns', None)
# 显示所有行
# pd.set_option('display.max_rows', None)

# 查看全部的列字段
columns = df.columns
print(columns)


def query_condition(dt, wh, update=0):
    # 查询条件
    data_condition = (df['dt'] == '2023-08-14') & (df["goods_id"] == 4488) & (df["end_stock_amount"] >= 0) & (df['predict_dt'] == dt) & (df['wh_dept_id'] == wh)
    query_data = df.loc[
        data_condition,
        ['goods_id', 'wh_dept_id', 'wh_name', 'end_stock_amount']
    ]

    print(query_data)

    if update == 1:
        # 修改数据
        df.loc[
            data_condition,
            # 赋值的字段
            'end_stock_amount'
        ] = 0

        # 数据写入文件
        # 不存储 index 信息: index=False
        df.to_csv(file_path, index=False)


data_dict = {
    '2023-08-13': [24701],
    '2023-08-14': [24701, 326919],
    '2023-08-15': [24701, 326919, 326921],
    '2023-08-16': [24701, 326919, 326921, 4001],
    '2023-08-17': [24701, 326919, 326921, 4001, 22001],
    '2023-08-18': [24701, 326919, 326921, 4001, 22001, 306601],
    '2023-08-19': [24701, 326919, 326921, 4001, 22001, 306601, 326920],
    '2023-08-20': [24701, 326919, 326921, 4001, 22001, 306601, 326920, 21701],
    '2023-08-21': [24701, 326919, 326921, 4001, 22001, 306601, 326920, 21701, 25601],
}


if __name__ == '__main__':
    # for dt_val in data_dict:
    #     for wh_id in data_dict[dt_val]:
    #         query_condition(dt_val, wh_id)
    query_condition('2023-08-13', 24701)
