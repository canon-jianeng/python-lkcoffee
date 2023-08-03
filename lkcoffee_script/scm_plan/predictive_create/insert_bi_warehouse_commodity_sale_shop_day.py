
import random
import pymysql
import yaml
import datetime
from lkcoffee_script import lk_tools

"""
查询是否重复


查询数据是否存在:


"""

# 去年到前一天的日期
now_year = int(datetime.datetime.now().strftime('%Y'))
date_list = lk_tools.datetool.get_year_date(now_year-1) + lk_tools.datetool.get_yesterday_last_date()
# print(date_list)

wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]

# 1:新品，2:常规
commodity_dict = {'1': [5990, 6192, 801], '2': [5352, 800]}

# 类型 10:自营售卖门店,20:联营售卖门店,30:合计
shop_type = ['10', '20', '30']

with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_insert = mysql_sql['insert_bi_warehouse_commodity_sale_shop_day']
sql_insert_value = mysql_sql['val_bi_warehouse_commodity_sale_shop_day']


val_data = ''
val_sql = sql_insert_value + ',\n'
amount = 0
for date_val in date_list:
    for wh in wh_dept_id:
        for mark_type in commodity_dict:
            for commodity_id in commodity_dict[mark_type]:
                for type_val in shop_type:
                    year_val = date_val.split('-')[0]
                    if type_val == '10':
                        shop_num = random.randint(10, 20)
                        amount += shop_num
                        val_str = val_sql.format(
                            wh, commodity_id, mark_type, type_val, year_val, date_val, shop_num+0.1
                        )
                        val_data += val_str
                    elif type_val == '20':
                        shop_num = random.randint(10, 20)
                        amount += shop_num
                        val_str = val_sql.format(
                            wh, commodity_id, mark_type, type_val, year_val, date_val, shop_num+0.1
                        )
                        val_data += val_str
                    elif type_val == '30':
                        val_str = val_sql.format(
                            wh, commodity_id, mark_type, type_val, year_val, date_val, amount+0.2
                        )
                        val_data += val_str
                        amount = 0
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/bi_warehouse_commodity_sale_shop_day.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
