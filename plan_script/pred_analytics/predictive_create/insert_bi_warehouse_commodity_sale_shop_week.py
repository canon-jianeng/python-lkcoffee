
import random
import pymysql
import yaml
import datetime
from lkcoffee_script import lk_tools

"""
查询是否重复


查询数据是否存在:


售卖门店数-实际(周纬度): t_bi_warehouse_commodity_sale_shop_week

"""

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))
# 当前日期
now_date = datetime.date.today()

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

# 打开数据库连接
db_cooperation = pymysql.connect(
    host=mysql_conf['cooperation']['host'],
    user=mysql_conf['cooperation']['user'],
    password=mysql_conf['cooperation']['pwd'],
    database=mysql_conf['cooperation']['db'],
    port=mysql_conf['cooperation']['port']
)

sql_insert = mysql_sql['insert_bi_warehouse_commodity_sale_shop_week']
sql_insert_value = mysql_sql['val_bi_warehouse_commodity_sale_shop_week']
sql_query = mysql_sql['query_prediction_week_config']
sql_query_amount = mysql_sql['query_bi_warehouse_commodity_sale_shop_day']

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_cooperation.cursor()

week_list = []
# 前一年的周范围列表
# cursor.execute(
#     sql_query.format(now_year-1)
# )
# data = cursor.fetchall()
# for date_val in data:
#     week_list.append(date_val)

# 当前年的周范围列表
cursor.execute(
    sql_query.format(now_year)
)
data = cursor.fetchall()
week_flag = 0
for date_val in data:
    if date_val[0] <= now_date <= date_val[1]:
        week_flag = 1
    if week_flag == 0:
        week_list.append(date_val)

# 后一年的周范围列表
cursor.execute(
    sql_query.format(now_year+1)
)
data = cursor.fetchall()
week_flag = 0
for date_val in data:
    if date_val[0] <= now_date <= date_val[1]:
        week_flag = 1
    if week_flag == 0:
        week_list.append(date_val)
print(week_list)

val_data = ''
val_sql = sql_insert_value + ',\n'
amount = 0
for week_val in week_list:
    year_val = week_val[0].strftime("%Y")
    for wh in wh_dept_id:
        for mark_type in commodity_dict:
            for commodity_id in commodity_dict[mark_type]:
                for type_val in shop_type:
                    if type_val == '10':
                        # 查询一周的数量
                        cursor.execute(
                            sql_query_amount.format(
                                week_val[0], week_val[1], wh, commodity_id, type_val
                            )
                        )
                        shop_num = cursor.fetchall()[0][0]
                        amount += shop_num
                        val_str = val_sql.format(
                            wh, commodity_id, mark_type, type_val,
                            year_val, week_val[2], shop_num
                        )
                        val_data += val_str
                    elif type_val == '20':
                        # 查询一周的日期列表
                        cursor.execute(
                            sql_query_amount.format(
                                week_val[0], week_val[1], wh, commodity_id, type_val
                            )
                        )
                        shop_num = cursor.fetchall()[0][0]
                        amount += shop_num
                        val_str = val_sql.format(
                            wh, commodity_id, mark_type, type_val,
                            year_val, week_val[2], shop_num
                        )
                        val_data += val_str
                    elif type_val == '30':
                        val_str = val_sql.format(
                            wh, commodity_id, mark_type, type_val,
                            year_val, week_val[2], amount
                        )
                        val_data += val_str
                        print(val_str)
                        amount = 0
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/bi_warehouse_commodity_sale_shop_week.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
