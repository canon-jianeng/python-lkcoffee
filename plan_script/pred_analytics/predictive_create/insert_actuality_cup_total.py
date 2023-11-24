
import random
import datetime
import yaml

"""
查询是否重复
SELECT * FROM t_actuality_cup_total GROUP BY `year`, wh_dept_id, type HAVING count(*) > 1;

查询数据是否存在:
SELECT * FROM t_actuality_cup_total 
WHERE
  `year`=2023 
  AND wh_dept_id in ('327193', '245971', '245871', '326932', '326327', '-1')
  AND type=10;

"""

# 当前年份
now_year = int(datetime.datetime.now().strftime('%Y'))
now_month = int(datetime.datetime.now().strftime('%m'))
# 年份列表
year_list = [now_year-1, now_year]

wh_dept_id = [
    '327193', '245971', '245871', '326932', '326327', '-1'
]

# 10: 饮品杯量, 20: 食品店日均, 30: 饮品杯量（新品/次新品）
# type_list = ['10', '20', '30']
type_list = ['30']

with open('./sql.yml', encoding='utf-8') as f:
    yml_data = yaml.load(f, Loader=yaml.CLoader)
    mysql_sql = yml_data['sql']
    mysql_conf = yml_data['mysql']

sql_insert = mysql_sql['insert_actuality_cup_total']
sql_insert_value = mysql_sql['val_actuality_cup_total']

val_data = ''
val_sql = sql_insert_value + ',\n'
for type_val in type_list:
    for year_val in year_list:
        if year_val == now_year:
            month_num = now_month - 1
        else:
            month_num = 12
        for wh in wh_dept_id:
            amount_1, amount_2, amount_3, amount_4, amount_5, amount_6 = 0, 0, 0, 0, 0, 0
            amount_7, amount_8, amount_9, amount_10, amount_11, amount_12 = 0, 0, 0, 0, 0, 0
            if month_num >= 1:
                amount_1 = random.uniform(20, 50)
            if month_num >= 2:
                amount_2 = random.uniform(20, 50)
            if month_num >= 3:
                amount_3 = random.uniform(20, 50)
            if month_num >= 4:
                amount_4 = random.uniform(20, 50)
            if month_num >= 5:
                amount_5 = random.uniform(20, 50)
            if month_num >= 6:
                amount_6 = random.uniform(20, 50)
            if month_num >= 7:
                amount_7 = random.uniform(20, 50)
            if month_num >= 8:
                amount_8 = random.uniform(20, 50)
            if month_num >= 9:
                amount_9 = random.uniform(20, 50)
            if month_num >= 10:
                amount_10 = random.uniform(20, 50)
            if month_num >= 11:
                amount_11 = random.uniform(20, 50)
            if month_num == 12:
                amount_12 = random.uniform(20, 50)
            amount_total = (amount_1 + amount_2 + amount_3 + amount_4 + amount_5 + amount_6
                            + amount_7 + amount_8 + amount_9 + amount_10 + amount_11 + amount_12) / 12
            val_str = val_sql.format(
                year_val, type_val, amount_1, amount_2, amount_3, amount_4,
                amount_5, amount_6, amount_7, amount_8, amount_9, amount_10,
                amount_11, amount_12, amount_total, wh
            )
            val_data += val_str

insert_data = sql_insert + '\n' + val_data


with open('../data/predictive_create/actuality_cup_total.txt', 'w', encoding='utf-8') as f:
    f.write(insert_data)
