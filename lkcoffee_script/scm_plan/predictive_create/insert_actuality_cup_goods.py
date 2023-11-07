
import random
import datetime
import datedays
import pymysql
import yaml
from lkcoffee_script import lk_tools

"""
查询是否重复
SELECT wh_dept_id, goods_id, type FROM t_actuality_cup_goods 
GROUP BY `year`, wh_dept_id, goods_id, type HAVING count(*) > 1;

查询数据是否存在:
SELECT * FROM t_actuality_cup_goods 
WHERE 
  `year`='2023' 
  AND wh_dept_id in ('327193', '245971', '245871', '326932', '326327', '-1') 
  AND goods_id in ('42', '48214', '82796', '44', '83070', '86969', '83207', '83622', '83623') 
  AND type in ('10', '20', '30', '40');

"""

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))
now_month = int(datetime.datetime.now().strftime('%m'))
# 年份列表
year_list = [now_year+1]
# year_list = [now_year-1, now_year, now_year+1]

goods_dict = {
    # 10:损耗率,20:实际消耗量,30:用售比系数,40:冷比例系数
    # 饮品
    # 新品有冷比例系数
    '42': ['10', '20', '40'],
    '48214': ['10', '20', '40'],
    # 冰杯, 用售比系数
    '82796': ['10', '20', '30', '40'],
    '44': ['10', '20'],
    '83070': ['10', '20'],
    '86969': ['10', '20'],
    '83207': ['10', '20'],
    # 食品
    '83622': ['10', '20'],
    '83623': ['10', '20']
}

wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]

with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']

sql_insert = mysql_sql['insert_actuality_cup_goods']
sql_insert_value = mysql_sql['val_actuality_cup_goods']

sql_query_cup = mysql_sql['query_actuality_cup_goods_day']


def get_month_num(year: int, month: int, wh_val, goods_id, type_val):
    end_date = lk_tools.datetool.get_month_days(year, month)
    # 查询一个月的数量
    cursor.execute(
        sql_query_cup.format(
            datetime.date(year, month, 1),
            datetime.date(year, month, end_date),
            wh_val, goods_id, type_val
        )
    )
    data_val = cursor.fetchall()
    return data_val[0][0]


with open('../predictive_analytics/predictive_sql.yml', encoding='utf-8') as f:
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


val_data = ''
val_sql = sql_insert_value + ',\n'
for year_val in year_list:
    if year_val == now_year:
        month_num = now_month - 1
    else:
        month_num = 12
    for wh in wh_dept_id:
        for item in goods_dict.items():
            for val in item[1]:
                if val == '10' or val == '30' or val == '40':
                    amount_1 = random.uniform(0, 1)
                    amount_2 = random.uniform(0, 1)
                    amount_3 = random.uniform(0, 1)
                    amount_4 = random.uniform(0, 1)
                    amount_5 = random.uniform(0, 1)
                    amount_6 = random.uniform(0, 1)
                    amount_7 = random.uniform(0, 1)
                    amount_8 = random.uniform(0, 1)
                    amount_9 = random.uniform(0, 1)
                    amount_10 = random.uniform(0, 1)
                    amount_11 = random.uniform(0, 1)
                    amount_12 = random.uniform(0, 1)
                    amount_total = (amount_1 + amount_2 + amount_3 + amount_4 + amount_5 + amount_6
                                    + amount_7 + amount_8 + amount_9 + amount_10 + amount_11 + amount_12)
                    val_str = val_sql.format(
                        year_val, item[0], val, amount_1, amount_2, amount_3, amount_4,
                        amount_5, amount_6, amount_7, amount_8, amount_9, amount_10,
                        amount_11, amount_12, amount_total, wh
                    )
                    val_data += val_str
                if val == '20':
                    amount_1, amount_2, amount_3, amount_4, amount_5, amount_6 = 0, 0, 0, 0, 0, 0
                    amount_7, amount_8, amount_9, amount_10, amount_11, amount_12 = 0, 0, 0, 0, 0, 0
                    if month_num >= 1:
                        amount_1 = get_month_num(year_val, 1, wh, item[0], val)
                    if month_num >= 2:
                        amount_2 = get_month_num(year_val, 2, wh, item[0], val)
                    if month_num >= 3:
                        amount_3 = get_month_num(year_val, 3, wh, item[0], val)
                    if month_num >= 4:
                        amount_4 = get_month_num(year_val, 4, wh, item[0], val)
                    if month_num >= 5:
                        amount_5 = get_month_num(year_val, 5, wh, item[0], val)
                    if month_num >= 6:
                        amount_6 = get_month_num(year_val, 6, wh, item[0], val)
                    if month_num >= 7:
                        amount_7 = get_month_num(year_val, 7, wh, item[0], val)
                    if month_num >= 8:
                        amount_8 = get_month_num(year_val, 8, wh, item[0], val)
                    if month_num >= 9:
                        amount_9 = get_month_num(year_val, 9, wh, item[0], val)
                    if month_num >= 10:
                        amount_10 = get_month_num(year_val, 10, wh, item[0], val)
                    if month_num >= 11:
                        amount_11 = get_month_num(year_val, 11, wh, item[0], val)
                    if month_num == 12:
                        amount_12 = get_month_num(year_val, 12, wh, item[0], val)
                    amount_total = (amount_1 + amount_2 + amount_3 + amount_4 + amount_5 + amount_6
                                    + amount_7 + amount_8 + amount_9 + amount_10 + amount_11 + amount_12)
                    val_str = val_sql.format(
                        year_val, item[0], val, amount_1, amount_2, amount_3, amount_4,
                        amount_5, amount_6, amount_7, amount_8, amount_9, amount_10,
                        amount_11, amount_12, amount_total, wh
                    )
                    val_data += val_str
                    print(val_str)
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/actuality_cup_goods.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
