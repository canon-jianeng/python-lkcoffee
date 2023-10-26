
import random
import pymysql
import yaml
import datetime
from lkcoffee_script import lk_tools

"""
查询是否重复


查询数据是否存在:
SELECT * FROM t_alg_new_warehouse_commodity_sale_shop WHERE commodity_id=6992 AND record_date LIKE '2024%'

售卖门店数-日纬度: t_alg_new_warehouse_commodity_sale_shop

"""


# 预测当前月及未来的3个月
# now_month = datetime.datetime.now().strftime('%Y-%m')
# date_list_pre = lk_tools.datetool.get_future_date(now_month, 3)

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))
# 未来数据
# 后一年日期
date_list_next_year = lk_tools.datetool.get_month_date(str(now_year+1)+'-12')
# 当前年日期（当前年1月1号到前一天日期的日期列表）
date_list_now = lk_tools.datetool.get_month_date(str(now_year)+'-12')

date_list = date_list_now + date_list_next_year


wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '245770', '-1'
]

# 新品
commodity_list = [5990, 6192, 801, 6967, 6973, 6991, 6992]


with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_insert = mysql_sql['insert_alg_new_warehouse_commodity_sale_shop']
sql_insert_value = mysql_sql['val_alg_new_warehouse_commodity_sale_shop']


val_data = ''
val_sql = sql_insert_value + ',\n'
self_num_total, agent_num_total = 0, 0
for date_val in date_list:
    for commodity_id in commodity_list:
        for wh in wh_dept_id:
            if wh == '-1':
                val_str = val_sql.format(
                    1, commodity_id, wh, date_val, self_num_total, agent_num_total
                )
                val_data += val_str
                self_num_total, agent_num_total = 0, 0
            else:
                self_num = random.randint(100, 300)
                agent_num = random.randint(10, self_num)
                # 汇总各个仓的门店数
                self_num_total += self_num
                agent_num_total += agent_num
                val_str = val_sql.format(
                    1, commodity_id, wh, date_val, self_num, agent_num
                )
                val_data += val_str
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/alg_new_warehouse_commodity_sale_shop.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
