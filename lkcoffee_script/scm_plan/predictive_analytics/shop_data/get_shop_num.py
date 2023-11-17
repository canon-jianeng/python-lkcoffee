
import datetime
import os.path

import yaml
import pymysql
import get_operating_num
from lkcoffee_script import lk_tools

"""
杯量预测: 只取营业门店数
算法预测: 优先取售卖门店数, 若没有售卖门店数, 则取营业门店数

"""


with open('../conf/predictive_sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

# 打开数据库连接
db_cooperation = pymysql.connect(
    host=mysql_conf['cooperation']['host'],
    user=mysql_conf['cooperation']['user'],
    password=mysql_conf['cooperation']['pwd'],
    database=mysql_conf['cooperation']['db'],
    port=mysql_conf['cooperation']['port']
)

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_cooperation.cursor()

sql_pred_shop = mysql_sql['query_pred_shop']
sql_actual_shop = mysql_sql['query_actual_shop']


def actual_wh_sale_shop(wh_id, date_val):
    # 实际售卖门店数
    date_tuple = date_val.split('-')
    cursor.execute(sql_actual_shop.format(wh_id, date_tuple[0]))
    data = cursor.fetchall()
    if len(data) > 0:
        shop_num = data[0][1]
    else:
        # 不存在售卖门店数, 则获取营业门店数
        shop_num = get_operating_num.cul_pred_operating_shop(wh_id, date_val)
    print(wh_id, shop_num)
    return shop_num


def pred_wh_sale_shop(wh_id, date_val, flag_country=0):
    # 预测售卖门店数
    cursor.execute(sql_actual_shop.format(wh_id, date_val))
    data = cursor.fetchall()
    if len(data) > 0:
        shop_num = data[0][1]
    else:
        # 不存在售卖门店数, 则获取营业门店数
        shop_num = get_operating_num.cul_pred_operating_shop(wh_id, date_val)
    print(wh_id, shop_num)
    return shop_num


if __name__ == '__main__':
    print(actual_wh_sale_shop('327193', '2023-10-10'))
