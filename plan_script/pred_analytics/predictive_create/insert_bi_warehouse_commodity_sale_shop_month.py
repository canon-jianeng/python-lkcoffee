
import random
import pymysql
import yaml
import datetime
from lkcoffee_script import lk_tools

"""
查询是否重复


查询数据是否存在:


售卖门店数-实际(月纬度): t_bi_warehouse_commodity_sale_shop_month

"""

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))
now_month = int(datetime.datetime.now().strftime('%m'))
# 当前日期
now_date = datetime.date.today()

wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]

# 1:新品，2:常规
# commodity_dict = {'1': [5990, 6192, 801], '2': [6976, 5352, 800]}
commodity_dict = {'2': [6976]}

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

sql_insert = mysql_sql['insert_bi_warehouse_commodity_sale_shop_month']
sql_insert_value = mysql_sql['val_bi_warehouse_commodity_sale_shop_month']
sql_query = mysql_sql['query_prediction_week_config']
sql_query_amount = mysql_sql['query_bi_warehouse_commodity_sale_shop_day']

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_cooperation.cursor()

# 年份列表
# year_list = [now_year-1, now_year, now_year+1]
year_list = [now_year, now_year+1]

def get_month_num(year: int, month: int, wh_val, commodity, type_int):
    end_date = lk_tools.datetool.get_month_days(year, month)
    # 查询一个月的数量
    cursor.execute(
        sql_query_amount.format(
            datetime.date(year, month, 1),
            datetime.date(year, month, end_date),
            wh_val, commodity, type_int
        )
    )
    data_val = cursor.fetchall()
    return data_val[0][0]


val_data = ''
val_sql = sql_insert_value + ',\n'
for year_val in year_list:
    if year_val == now_year:
        month_num = now_month - 1
    else:
        month_num = 12
    for wh in wh_dept_id:
        for mark_type in commodity_dict:
            for commodity_id in commodity_dict[mark_type]:
                for type_val in shop_type:
                    january_num, february_num, march_num, april_num, may_num, june_num = 0, 0, 0, 0, 0, 0
                    july_num, august_num, september_num, october_num, november_num, december_num = 0, 0, 0, 0, 0, 0
                    if month_num >= 1:
                        january_num = get_month_num(year_val, 1, wh, commodity_id, type_val)
                    if month_num >= 2:
                        february_num = get_month_num(year_val, 2, wh, commodity_id, type_val)
                    if month_num >= 3:
                        march_num = get_month_num(year_val, 3, wh, commodity_id, type_val)
                    if month_num >= 4:
                        april_num = get_month_num(year_val, 4, wh, commodity_id, type_val)
                    if month_num >= 5:
                        may_num = get_month_num(year_val, 5, wh, commodity_id, type_val)
                    if month_num >= 6:
                        june_num = get_month_num(year_val, 6, wh, commodity_id, type_val)
                    if month_num >= 7:
                        july_num = get_month_num(year_val, 7, wh, commodity_id, type_val)
                    if month_num >= 8:
                        august_num = get_month_num(year_val, 8, wh, commodity_id, type_val)
                    if month_num >= 9:
                        september_num = get_month_num(year_val, 9, wh, commodity_id, type_val)
                    if month_num >= 10:
                        october_num = get_month_num(year_val, 10, wh, commodity_id, type_val)
                    if month_num >= 11:
                        november_num = get_month_num(year_val, 11, wh, commodity_id, type_val)
                    if month_num == 12:
                        december_num = get_month_num(year_val, 12, wh, commodity_id, type_val)
                    total_amount = january_num + february_num + march_num + april_num + may_num
                    total_amount += june_num + july_num + august_num + september_num + october_num
                    total_amount += november_num + december_num
                    val_str = val_sql.format(
                        wh, commodity_id, mark_type, type_val, year_val,
                        january_num, february_num, march_num, april_num, may_num, june_num,
                        july_num, august_num, september_num, october_num, november_num, december_num,
                        total_amount
                    )
                    val_data += val_str
                    print(val_str)
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/bi_warehouse_commodity_sale_shop_month.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
