
import random
import datetime
import yaml
import pymysql
from lkcoffee_script import lk_tools

"""
查询是否重复
SELECT wh_dept_id, week_id FROM t_actuality_cup_total_week 
GROUP BY wh_dept_id, week_id HAVING count(*) > 1;

查询数据是否存在:
SELECT wh_dept_id, week_id FROM t_actuality_cup_total_week 
WHERE
  wh_dept_id in ('327193', '245971', '245871', '326932', '326327', '-1') 
  AND week_id in ();

"""

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))
# 当前日期
now_date = datetime.date.today()

wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]

type_list = ['10', '20']

with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_insert = mysql_sql['insert_actuality_cup_total_week']
sql_insert_value = mysql_sql['val_actuality_cup_total_week']

sql_query = mysql_sql['query_prediction_week_config']
sql_query_id = mysql_sql['query_prediction_week_config_id']

# 打开数据库连接
db_cooperation = pymysql.connect(
    host=mysql_conf['cooperation']['host'],
    user=mysql_conf['cooperation']['user'],
    password=mysql_conf['cooperation']['pwd'],
    database=mysql_conf['cooperation']['db'],
    port=mysql_conf['cooperation']['port']
)

key_list = ['self_num', 'agent_num', 'total_num', 'self_operating_num', 'agent_operating_num', 'total_operating_num']

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db_cooperation.cursor()

week_list = []
# 前一年的周范围列表
cursor.execute(
    sql_query.format(now_year-1)
)
data = cursor.fetchall()
for date_val in data:
    week_list.append(date_val)

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
# print(week_list)


def get_week_range():
    # 当天日期往前30天的日期列表
    date_list = lk_tools.datetool.get_last_date(30)
    cursor.execute(
        sql_query.format(datetime.datetime.now().strftime('%Y'))
    )
    data_tuple = cursor.fetchall()
    week_id_end = ''
    week_id_start = ''
    week_start = datetime.datetime.strptime(date_list[len(date_list)-1], '%Y-%m-%d').date()
    week_end = datetime.datetime.strptime(date_list[0], '%Y-%m-%d').date()
    for date_val in data_tuple:
        if date_val[0] < week_start < date_val[1]:
            week_id_end = date_val[2]
        if date_val[0] < week_end < date_val[1]:
            week_id_start = date_val[2]
    cursor.execute(sql_query_id.format(week_id_start, week_id_end))
    data_tuple = cursor.fetchall()
    week_date_list = []
    for week_id in data_tuple:
        week_date_list.append(week_id[0])
    print(week_date_list)


val_data = ''
val_sql = sql_insert_value + ',\n'
for type_val in type_list:
    for wh in wh_dept_id:
        for week_val in week_list:
            amount = random.uniform(0, 20)
            val_str = val_sql.format(
                week_val[2], wh, type_val, amount
            )
            val_data += val_str

insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/actuality_cup_total_week.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
