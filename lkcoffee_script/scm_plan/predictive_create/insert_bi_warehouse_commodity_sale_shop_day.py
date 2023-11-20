
import random
import pymysql
import yaml
import datetime
from decimal import Decimal
from lkcoffee_script import lk_tools

"""
查询是否重复


查询数据是否存在:


售卖门店数-实际(日纬度): t_bi_warehouse_commodity_sale_shop_day

"""

now_year = int(datetime.datetime.now().strftime('%Y'))

# 去年到前一天的日期
# date_list = lk_tools.datetool.get_year_date(now_year-1) + lk_tools.datetool.get_yesterday_last_date()
# print(date_list)

# 前一年日期
date_list_last_year = lk_tools.datetool.get_month_date(str(now_year-1)+'-12')
# 当前年日期
date_list_now = lk_tools.datetool.get_month_date(str(now_year)+'-12')
# 明年日期
date_list_next_year = lk_tools.datetool.get_month_date(str(now_year+1)+'-12')
# date_list = date_list_last_year + date_list_now + date_list_next_year
date_list = date_list_now + date_list_next_year

wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]

# 1:新品，2:常规
commodity_dict = {'1': [5990, 6192, 801], '2': [6976, 5352, 800]}

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
shop_num3 = 0
shop_num_total1, shop_num_total2, shop_num_total3 = 0, 0, 0
for date_val in date_list:
    for wh in wh_dept_id:
        for mark_type in commodity_dict:
            for commodity_id in commodity_dict[mark_type]:
                for type_val in shop_type:
                    year_val = date_val.split('-')[0]
                    if type_val == '10':
                        if wh == '-1':
                            val_str = val_sql.format(
                                wh, commodity_id, mark_type, type_val, year_val, date_val, shop_num_total1
                            )
                            val_data += val_str
                            shop_num_total1 = 0
                        else:
                            shop_num1 = Decimal(random.randint(20, 30) + Decimal('0.1'))
                            shop_num3 += shop_num1
                            shop_num_total1 += shop_num1
                            val_str = val_sql.format(
                                wh, commodity_id, mark_type, type_val, year_val, date_val, shop_num1
                            )
                            val_data += val_str
                    elif type_val == '20':
                        if wh == '-1':
                            val_str = val_sql.format(
                                wh, commodity_id, mark_type, type_val, year_val, date_val, shop_num_total2
                            )
                            val_data += val_str
                            shop_num_total2 = 0
                        else:
                            shop_num2 = Decimal(random.randint(20, 30) + Decimal('0.1'))
                            shop_num3 += shop_num2
                            shop_num_total2 += shop_num2
                            val_str = val_sql.format(
                                wh, commodity_id, mark_type, type_val, year_val, date_val, shop_num2
                            )
                            val_data += val_str
                    elif type_val == '30':
                        if wh == '-1':
                            val_str = val_sql.format(
                                wh, commodity_id, mark_type, type_val, year_val, date_val, shop_num_total3
                            )
                            val_data += val_str
                            shop_num_total3 = 0
                        else:
                            shop_num_total3 += shop_num3
                            val_str = val_sql.format(
                                wh, commodity_id, mark_type, type_val, year_val, date_val, shop_num3
                            )
                            val_data += val_str
                            shop_num3 = 0
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/bi_warehouse_commodity_sale_shop_day.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
