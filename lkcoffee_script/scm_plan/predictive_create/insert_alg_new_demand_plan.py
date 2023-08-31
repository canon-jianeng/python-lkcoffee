
import random
import pymysql
import yaml
import datetime
from lkcoffee_script import lk_tools

"""
查询是否重复


查询数据是否存在:


"""


# 预测当前月及未来的3个月
now_month = datetime.datetime.now().strftime('%Y-%m')
date_list_pre = lk_tools.datetool.get_future_date(now_month, 3)

wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '245770'
]

# 新品
# goods_list = [46, 83625, 83077]
goods_list = [83626, 3077, 3080]

with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_insert = mysql_sql['insert_alg_new_demand_plan']
sql_insert_value = mysql_sql['val_alg_new_demand_plan']


val_data = ''
val_sql = sql_insert_value + ',\n'
for date_val in date_list_pre:
    for wh in wh_dept_id:
        for goods_id in goods_list:
            pred_shop_consume = 1000
            pred_shop_order = 2000
            pred_wh_consume = 3000
            pred_wh_cg = 4000
            val_str = val_sql.format(
                wh, goods_id, date_val,
                pred_shop_consume, pred_shop_order,
                pred_wh_consume, pred_wh_cg
            )
            val_data += val_str
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/alg_new_demand_plan.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
