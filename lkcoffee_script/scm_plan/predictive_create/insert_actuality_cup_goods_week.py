
import random
import yaml
import pymysql
import datetime

"""
查询是否重复
SELECT week_id, wh_dept_id, goods_id, type 
FROM t_actuality_cup_goods_week 
GROUP BY week_id, wh_dept_id, goods_id, type HAVING count(*) > 1;

查询数据是否存在:
SELECT * FROM t_actuality_cup_goods_week 
WHERE
  wh_dept_id in ('327193', '245971', '245871', '326932', '326327', '-1') 
  AND goods_id in ('42','48214','82796','44','83070', '83622', '83623') 
  AND week_id in () 
  AND type in ('20', '40');

"""

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))
# 当前日期
now_date = datetime.date.today()

wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]

goods_dict = {
    # 新品有冷比例系数
    '42': ['20', '40'],
    '48214': ['20', '40'],
    '82796': ['20', '40'],
    '44': ['20'],
    '83070': ['20'],
    # 食品
    '83622': ['20'],
    '83623': ['20']
}


with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_insert = mysql_sql['insert_actuality_cup_goods_week']
sql_insert_value = mysql_sql['val_actuality_cup_goods_week']

sql_query = mysql_sql['query_prediction_week_config']
sql_query_cup_day = mysql_sql['query_actuality_cup_goods_day']


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
for date_val in data:
    week_list.append(date_val)
# print(week_list)


val_data = ''
val_sql = sql_insert_value + ',\n'
for wh in wh_dept_id:
    for item in goods_dict.items():
        for val in item[1]:
            for week_val in week_list:
                if val == '20':
                    # 查询一周的数量
                    cursor.execute(
                        sql_query_cup_day.format(
                            week_val[0], week_val[1], wh, item[0], val
                        )
                    )
                    week_amount = cursor.fetchall()[0][0]
                    val_str = val_sql.format(
                        week_val[2], wh, item[0], val, week_amount
                    )
                    val_data += val_str
                    print(val_str)
                if val == '40':
                    week_amount = random.uniform(0, 1)
                    val_str = val_sql.format(
                        week_val[2], wh, item[0], val, week_amount
                    )
                    val_data += val_str
insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/actuality_cup_goods_week.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)

