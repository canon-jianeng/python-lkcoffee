
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
    '327193', '245971', '245871', '326932', '326327', '-1'
]

# 新品
commodity_list = [5990, 6192, 801]

with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_insert = mysql_sql['insert_alg_new_warehouse_commodity_sale_shop']
sql_insert_value = mysql_sql['val_alg_new_warehouse_commodity_sale_shop']


val_data = ''
val_sql = sql_insert_value + ',\n'
for date_val in date_list_pre:
    for wh in wh_dept_id:
        for commodity_id in commodity_list:
            self_num = random.randint(100, 300)
            agent_num = random.randint(10, self_num)
            val_str = val_sql.format(
                1, commodity_id, wh, date_val, self_num, agent_num
            )
            val_data += val_str
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/alg_new_warehouse_commodity_sale_shop.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
