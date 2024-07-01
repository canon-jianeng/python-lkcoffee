
import warnings
from datetime import datetime
import pandas as pd


def compare_dates(file_path, field_list):
    # 读取Excel文件
    with warnings.catch_warnings(record=True):
        df = pd.read_excel(file_path, engine='openpyxl', sheet_name='sheet1')
    # 显示数据框内容
    for index, row in df.iterrows():
        str1 = row[field_list[0]]
        str2 = row[field_list[1]]
        if '外' in str(str1):
            str1 = str(str1).replace('外', '')
        elif '补' in str(str1):
            str1 = str(str1).replace('补', '')
        if '外' in str(str2):
            str2 = str(str2).replace('外', '')
        elif '补' in str(str2):
            str2 = str(str2).replace('补', '')
        if index > 1 and not pd.isna(str1) and not pd.isna(str2):
            str1 = datetime.strptime(str1, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d')
            str2 = datetime.strptime(str2, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d')
            if str1 != str2:
                print(str1, str2, index+1)


if __name__ == '__main__':
    compare_list = [
        ['班段1签到时间', '班段1签退时间'],
        ['班段2签到时间', '班段2签退时间'],
        ['班段3签到时间', '班段3签退时间'],
        ['班段4签到时间', '班段4签退时间']
    ]
    for field_list in compare_list:
        print(field_list)
        compare_dates(
            '../data/日报(2024-06-01-2024-06-30).xlsx',
            field_list
        )
